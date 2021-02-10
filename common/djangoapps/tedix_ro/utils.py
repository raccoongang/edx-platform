"""
Helper Methods
"""
import json
import hashlib
import time

from django.core.exceptions import ImproperlyConfigured
from urlparse import urljoin

from babel.dates import format_datetime
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext as _

from courseware.models import StudentModule
from lms.djangoapps.grades.config.models import PersistentGradesEnabledFlag
from lms.djangoapps.grades.course_data import CourseData
from lms.djangoapps.grades.course_grade import CourseGrade
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from xmodule.modulestore.django import modulestore

from util.request import course_id_from_url


def get_payment_link(user):
    if not user:
        return ''
    return 'http://tedix.kloudstores.com/?email={email}&type=student'.format(
        email=user.email
    )


def get_common_possible(user, course):
        """
        Get possible score for each problem in a course.

        Arguments:
            - user (obj): django model User.
            - course (obj): coursemodule instance
        Return dict {'block_id': <possible_score>}.
        """
        course_grade = CourseGradeFactory().read(user, course)
        courseware_summary = course_grade.chapter_grades.values()
        score_mapping = {}
        for chapter in courseware_summary:
            for section in chapter['sections']:
                for problem, score in section.problem_scores.items():
                    score_mapping[problem.block_id] = int(score.possible)
        
        return score_mapping


def report_data_preparation(user, course):
    """
    Takes user and course
    Return "report_data" - data for extended report
    """
    Question = apps.get_model('tedix_ro', 'Question')
    questions_data = []
    header = []
    video_questions = Question.objects.filter(video_lesson__course=course.id)
    total_earned = 0
    raw_possible = 0
    raw_earned = 0
    video_earned_count = 0
    video_possible_count = 0

    questions = video_questions.values('question_id', 'video_lesson__video_id').distinct()
    user_video_questions = video_questions.filter(video_lesson__user=user)

    if user_video_questions:
        for video_question in user_video_questions:
            questions = questions.exclude(video_lesson__video_id=video_question.video_lesson.video_id)
            header.append((video_question.question_id, 'video_lesson'))
            score_info = {
                'earned': 0,
                'possible': 1
            }
            raw_possible += 1
            video_earned_count += 1 if video_question.attempt_count > 0 else 0
            video_possible_count += 1

            if video_question.attempt_count == 1:
                total_earned += 1
                score_info['earned'] = 1
                raw_earned += 1

            questions_data.append({
                'title': video_question.question_id,
                'attempts': video_question.attempt_count,
                'done': True,
                'type': 'video_lesson',
                'score_info': score_info
            })
    else:
        for question in questions:
            question_id = question.get('question_id')
            header.append((question_id, 'video_lesson'))
            score_info = {
                'earned': 0,
                'possible': 1
            }
            raw_possible += 1
            video_possible_count += 1
            questions_data.append({
                'title': question_id,
                'attempts': 0,
                'done': False,
                'type': 'video_lesson',
                'score_info': score_info
            })

    course_complete_list = []

    # in case when StudentModule does not exist we get possible score from here
    common_possible = get_common_possible(user, course)
            

    # this huge loop is only for getting problem's display_name, otherwise we could use StudentModule instances
    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                for problem in unit.get_children():
                    if problem.location.block_type == 'problem':
                        student_module = StudentModule.objects.filter(student=user, module_state_key=problem.location).first()
                        score_info = {}
                        if student_module:
                            student_module_state = json.loads(student_module.state)
                            score = student_module_state['score']
                            attempts = student_module_state.get('attempts', 0)

                            # done means an answer was submitted
                            done = student_module_state.get('done')
                            course_complete_list.append(done)

                            if attempts == 1:
                                raw_earned += score['raw_earned']

                            raw_possible += score['raw_possible']
                            score_info = {
                                'earned': score['raw_earned'],
                                'possible': score['raw_possible'],
                                'done': done
                            }
                        else:
                            score_info = {
                                'earned': 0,
                                'possible': common_possible[problem.location.block_id],
                                'done': False
                            }
                            raw_possible += common_possible[problem.location.block_id]

                        header.append((problem.display_name, 'problem'))
                        questions_data.append({
                            'title': problem.display_name,
                            'type': 'problem',
                            'score_info': score_info,
                        })

    percent = (float(raw_earned) / raw_possible) * 10 if raw_possible else 0
    report_data = {
        'full_name': user.profile.name or user.username,
        'completion': len(course_complete_list) > 0 and all(course_complete_list) and video_earned_count >= video_possible_count,
        'questions': questions_data,
        'earned': raw_earned,
        'percent': '{} ({} {} {})'.format(round(percent, 2) or 0, raw_earned, _('out of'), raw_possible) if percent else 'n/a',
    }
    return header, report_data


def get_all_questions_count(course_key):
    """
    Return a number off all questions in a course including video lessons.
    """
    Question = apps.get_model('tedix_ro', 'Question')
    questions_count = Question.objects.filter(video_lesson__course=course_key).values('question_id', 'video_lesson__video_id').distinct().count()

    student_modules = StudentModule.objects.filter(course_id=course_key, module_type='problem')
    all_q = 0

    for student_module in student_modules:
        student_module_state = json.loads(student_module.state)
        raw_possible = student_module_state['score']['raw_possible']

        all_q += raw_possible
    return all_q + questions_count


def get_points_earned_possible(course_key, user_id=None, user=None):
    """
    Get points earned and possible for a user in the certain course.
    
    Arguments:
        user_id (int)
        user (obj): Django model User or user_id
        course_key (obj): CourseKeyField
    Return:
        earned (int): points the user earned.
        possible (int): points possible in the course.
        complete (bool): whether all problem were submitted.
    """
    assert user_id is not None or user is not None

    user_id = user_id or user.id

    Question = apps.get_model('tedix_ro', 'Question')
    questions = Question.objects.filter(video_lesson__course=course_key, video_lesson__user=user_id)
    possible_questions_by_course = Question.objects.filter(video_lesson__course=course_key).values_list('question_id').distinct().count()
    possible = possible_questions_by_course
    earned = questions.filter(attempt_count=1).count()
    student_modules = StudentModule.objects.filter(student=user_id, course_id=course_key, module_type='problem')
    complete_list = []

    if student_modules:
        for student_module in student_modules:
            student_module_state = json.loads(student_module.state)
            attempts = student_module_state.get('attempts', 0)
            raw_possible = student_module_state['score']['raw_possible']
            raw_earned = student_module_state['score']['raw_earned']

            complete_list.append(student_module_state.get('done'))

            possible += raw_possible
            if attempts == 1:
                earned += raw_earned
    else: # when student didn't get to the lesson page
        course = modulestore().get_course(course_key)
        user = user or User.objects.get(id=user_id)
        common_possible_for_course = get_common_possible(user, course)
        possible += int(sum(common_possible_for_course.values()))

    return earned, possible, len(complete_list) > 0 and all(complete_list)


def light_report_data_preparation(user, course):
    Question = apps.get_model('tedix_ro', 'Question')
    StudentCourseDueDate = apps.get_model('tedix_ro', 'StudentCourseDueDate')
    count_answer_first_attempt = 0
    completion = True
    count_questions = 0

    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                for problem in unit.get_children():
                    if problem.location.block_type == 'problem':
                        student_module = StudentModule.objects.filter(
                            student=user,
                            module_state_key=problem.location
                        ).first()
                        if student_module:
                            attempts = json.loads(student_module.state).get("attempts", 0)
                            if attempts == 1:
                                count_answer_first_attempt += 1
                            if attempts == 0:
                                completion = False
                        else:
                            completion = False
                        count_questions += 1
    count_questions += Question.objects.filter(video_lesson__course=course.id).values('question_id').distinct().count()
    count_answer_first_attempt += Question.objects.filter(video_lesson__course=course.id, video_lesson__user=user, attempt_count=1).count()
    student_course_due_date = StudentCourseDueDate.objects.filter(student__user=user, course_id=course.id).first()
    due_date = student_course_due_date.due_date if student_course_due_date else None
    report_data = {
        'student_name': user.profile.name or user.username,
        'lesson': course.display_name,
        'completion': completion,
        'count_answer_first_attempt': count_answer_first_attempt,
        'count_questions': count_questions,
        'percent': (count_answer_first_attempt * 100 / count_questions) if count_questions else 100,
        'due_date': format_datetime(due_date, "yy.MM.dd hh:mm a", locale='en') if due_date else 'N/A',
        'report_url': urljoin(
            configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            reverse('extended_report', kwargs={'course_key': course.id})
        )
    }
    return report_data


def lesson_course_grade(user, course_key):
    """
    Return "CourseGrade" object for "user" and "course_key"
    """
    if PersistentGradesEnabledFlag.feature_enabled(course_key):
        course_grade = CourseGradeFactory().read(user=user, course_key=course_key)
    else:
        course_data = CourseData(user, course_key=course_key)
        course_grade = CourseGrade(
            user,
            course_data
        )
        course_grade = course_grade.update()
    return course_grade


def all_problems_have_answer(user, course_grade):
    """
    Return "True" if all problems have attempts
    """
    if course_grade.problem_scores:
        for problem in course_grade.problem_scores:
            student_module = StudentModule.objects.filter(
                student=user,
                module_state_key=problem
            ).first()
            if not student_module or not json.loads(student_module.state).get("done"):
                return False
        return True
    return False


def video_lesson_completed(user, course_key):
    """
    Return "True" if all question in video lesson has attempts
    """
    Question = apps.get_model('tedix_ro', 'Question')
    video_questions = Question.objects.filter(video_lesson__course=course_key)
    questions_count = video_questions.values('question_id').distinct().count()
    answered_questions_count = video_questions.filter(video_lesson__user=user).exclude(attempt_count=0).count()
    return questions_count == answered_questions_count


def reset_student_progress(user, course_key):
    VideoLesson = apps.get_model('tedix_ro', 'VideoLesson')
    StudentReportSending = apps.get_model('tedix_ro', 'StudentReportSending')
    VideoLesson.objects.filter(user=user, course=course_key).delete()
    StudentModule.objects.filter(course_id=course_key, student=user).delete()
    StudentReportSending.objects.filter(course_id=course_key, user=user).delete()


def encrypted_user_data(request):
    """
    Provide special user data to be handled by a third party frontend application.
    Arguments:
     - request: WSGI request object
    Return:
        Json object with the following data:
          - created (int): Timestamp user.date_joined.
          - id (str): md5 hashed username.
          - usertype (str): "student"/"staff"/"null".
          - lesson_is_active_homework (bool): 
            true if the user has homework (StudentCourseDueDate) for a course and the due date did not pass yet.
    """
    StudentCourseDueDate = apps.get_model('tedix_ro', 'StudentCourseDueDate')
    user = request.user
    lesson_is_active_homework = None
    user_id = None
    created = None
    user_type = None
    salt = 'tedix-user'

    if user.is_authenticated:
        created = time.mktime(user.date_joined.timetuple())
        m = hashlib.md5()
        m.update(user.username)
        m.update(salt)
        user_id = m.hexdigest()
        user_type = 'student' if hasattr(user, 'studentprofile') else 'staff'
        course_id = course_id_from_url(request.get_full_path())
        lesson_is_active_homework = False
        if course_id:
            lesson_is_active_homework = StudentCourseDueDate.is_active(user, course_id)

    return json.dumps({
        'created': int(created) if created is not None else None,
        'id': user_id,
        'usertype': user_type,
        'lesson_is_active_homework': lesson_is_active_homework,
    })
