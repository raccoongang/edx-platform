# Compute grades using real division, with no integer truncation
from __future__ import division
from collections import defaultdict
from functools import partial
import json
import logging

from contextlib import contextmanager
from django.db import transaction
from django.test.client import RequestFactory

import dogstats_wrapper as dog_stats_api

from courseware import courses
from courseware.model_data import FieldDataCache
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from .models import StudentModule
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.signals.signals import GRADES_UPDATED


log = logging.getLogger("edx.courseware")


def descriptor_affects_grading(block_types_affecting_grading, descriptor):
    """
    Returns True if the descriptor could have any impact on grading, else False.

    Something might be a scored item if it is capable of storing a score
    (has_score=True). We also have to include anything that can have children,
    since those children might have scores. We can avoid things like Videos,
    which have state but cannot ever impact someone's grade.
    """
    return descriptor.location.block_type in block_types_affecting_grading


def field_data_cache_for_grading(course, user):
    """
    Given a CourseDescriptor and User, create the FieldDataCache for grading.

    This will generate a FieldDataCache that only loads state for those things
    that might possibly affect the grading process, and will ignore things like
    Videos.
    """
    descriptor_filter = partial(descriptor_affects_grading, course.block_types_affecting_grading)
    return FieldDataCache.cache_for_descriptor_descendents(
        course.id,
        user,
        course,
        depth=None,
        descriptor_filter=descriptor_filter
    )


def answer_distributions(course_key):
    """
    Given a course_key, return answer distributions in the form of a dictionary
    mapping:

      (problem url_name, problem display_name, problem_id) -> {dict: answer -> count}

    Answer distributions are found by iterating through all StudentModule
    entries for a given course with type="problem" and a grade that is not null.
    This means that we only count LoncapaProblems that people have submitted.
    Other types of items like ORA or sequences will not be collected. Empty
    Loncapa problem state that gets created from runnig the progress page is
    also not counted.

    This method accesses the StudentModule table directly instead of using the
    CapaModule abstraction. The main reason for this is so that we can generate
    the report without any side-effects -- we don't have to worry about answer
    distribution potentially causing re-evaluation of the student answer. This
    also allows us to use the read-replica database, which reduces risk of bad
    locking behavior. And quite frankly, it makes this a lot less confusing.

    Also, we're pulling all available records from the database for this course
    rather than crawling through a student's course-tree -- the latter could
    potentially cause us trouble with A/B testing. The distribution report may
    not be aware of problems that are not visible to the user being used to
    generate the report.

    This method will try to use a read-replica database if one is available.
    """
    # dict: { module.module_state_key : (url_name, display_name) }
    state_keys_to_problem_info = {}  # For caching, used by url_and_display_name

    def url_and_display_name(usage_key):
        """
        For a given usage_key, return the problem's url and display_name.
        Handle modulestore access and caching. This method ignores permissions.

        Raises:
            InvalidKeyError: if the usage_key does not parse
            ItemNotFoundError: if there is no content that corresponds
                to this usage_key.
        """
        problem_store = modulestore()
        if usage_key not in state_keys_to_problem_info:
            problem = problem_store.get_item(usage_key)
            problem_info = (problem.url_name, problem.display_name_with_default)
            state_keys_to_problem_info[usage_key] = problem_info

        return state_keys_to_problem_info[usage_key]

    # Iterate through all problems submitted for this course in no particular
    # order, and build up our answer_counts dict that we will eventually return
    answer_counts = defaultdict(lambda: defaultdict(int))
    for module in StudentModule.all_submitted_problems_read_only(course_key):
        try:
            state_dict = json.loads(module.state) if module.state else {}
            raw_answers = state_dict.get("student_answers", {})
        except ValueError:
            log.error(
                u"Answer Distribution: Could not parse module state for StudentModule id=%s, course=%s",
                module.id,
                course_key,
            )
            continue

        try:
            url, display_name = url_and_display_name(module.module_state_key.map_into_course(course_key))
            # Each problem part has an ID that is derived from the
            # module.module_state_key (with some suffix appended)
            for problem_part_id, raw_answer in raw_answers.items():
                # Convert whatever raw answers we have (numbers, unicode, None, etc.)
                # to be unicode values. Note that if we get a string, it's always
                # unicode and not str -- state comes from the json decoder, and that
                # always returns unicode for strings.
                answer = unicode(raw_answer)
                answer_counts[(url, display_name, problem_part_id)][answer] += 1

        except (ItemNotFoundError, InvalidKeyError):
            msg = "Answer Distribution: Item {} referenced in StudentModule {} " + \
                  "for user {} in course {} not found; " + \
                  "This can happen if a student answered a question that " + \
                  "was later deleted from the course. This answer will be " + \
                  "omitted from the answer distribution CSV."
            log.warning(
                msg.format(module.module_state_key, module.id, module.student_id, course_key)
            )
            continue

    return answer_counts


@transaction.commit_manually
def grade(student, request, course, keep_raw_scores=False, field_data_cache=None, scores_client=None):
    """
    Wraps "_grade" with the manual_transaction context manager just in case
    there are unanticipated errors.
    Send a signal to update the minimum grade requirement status.
    """
    with manual_transaction():
        grade_summary = course.grading.grade(student, request, course, keep_raw_scores, field_data_cache, scores_client)
        responses = GRADES_UPDATED.send_robust(
            sender=None,
            username=request.user.username,
            grade_summary=grade_summary,
            course_key=course.id,
            deadline=course.end
        )

        for receiver, response in responses:
            log.info('Signal fired when student grade is calculated. Receiver: %s. Response: %s', receiver, response)

        return grade_summary


@transaction.commit_manually
def progress_summary(student, request, course, field_data_cache=None, scores_client=None):
    """
    Wraps "_progress_summary" with the manual_transaction context manager just
    in case there are unanticipated errors.
    """
    with manual_transaction():
        return course.grading.progress_summary(student, request, course, field_data_cache, scores_client)


@contextmanager
def manual_transaction():
    """A context manager for managing manual transactions"""
    try:
        yield
    except Exception:
        transaction.rollback()
        log.exception('Due to an error, this transaction has been rolled back')
        raise
    else:
        transaction.commit()


def iterate_grades_for(course_or_id, students, keep_raw_scores=False):
    """Given a course_id and an iterable of students (User), yield a tuple of:

    (student, gradeset, err_msg) for every student enrolled in the course.

    If an error occurred, gradeset will be an empty dict and err_msg will be an
    exception message. If there was no error, err_msg is an empty string.

    The gradeset is a dictionary with the following fields:

    - grade : A final letter grade.
    - percent : The final percent for the class (rounded up).
    - section_breakdown : A breakdown of each section that makes
        up the grade. (For display)
    - grade_breakdown : A breakdown of the major components that
        make up the final grade. (For display)
    - raw_scores: contains scores for every graded module
    """
    if isinstance(course_or_id, (basestring, CourseKey)):
        course = courses.get_course_by_id(course_or_id)
    else:
        course = course_or_id

    # We make a fake request because grading code expects to be able to look at
    # the request. We have to attach the correct user to the request before
    # grading that student.
    request = RequestFactory().get('/')

    for student in students:
        with dog_stats_api.timer('lms.grades.iterate_grades_for', tags=[u'action:{}'.format(course.id)]):
            try:
                request.user = student
                # Grading calls problem rendering, which calls masquerading,
                # which checks session vars -- thus the empty session dict below.
                # It's not pretty, but untangling that is currently beyond the
                # scope of this feature.
                request.session = {}
                gradeset = grade(student, request, course, keep_raw_scores)
                yield student, gradeset, ""
            except Exception as exc:  # pylint: disable=broad-except
                # Keep marching on even if this student couldn't be graded for
                # some reason, but log it for future reference.
                log.exception(
                    'Cannot grade student %s (%s) in course %s because of exception: %s',
                    student.username,
                    student.id,
                    course.id,
                    exc.message
                )
                yield student, {}, exc.message
