import json
import logging

from django.contrib.auth.models import User
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from django.utils.translation import ugettext as _
from django.utils.timezone import localtime, activate, deactivate

from courseware.courses import get_course_by_id
from openedx.core.djangoapps.content.course_structures.models import CourseStructure
from student.views import get_course_enrollments
from student.models import CourseEnrollment, UserProfile
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from courseware import models
from ccx.utils import get_course_chapters

log = logging.getLogger(__name__)

"""
This module creates data for csv report with list of course users. Returns dictionary {'header':header, 'data':data}
"""


def _find_course(course_key, courses):
    """
    Checks if course with given key exists in list of all courses.
    If the course does not exist returns None.
    If the course exist returns course descriptor.

    Args:
        course_key (CourseLocator): the course key
        courses : an iterable list of courses
    Returns:
        None: If the course does not exist
        course: course descriptor
    """
    if course_key in courses:
        course = courses[course_key]
        return course
    try:
        course = get_course_by_id(course_key)
        return course
    except Exception:   # pylint: disable=broad-except
        return None


def _get_children(parent, course_ordered):
    """
    Method for getting children from course structure object

    Args:
        parent: usage key of course structure element (e.g. module_state_key), for example:
        u'block-v1:edX+DemoX+Demo_Course+type@vertical+block@4e592689563243c484af947465eaef0d'
        course_ordered: (OrderedDict) the blocks of course structure object in the order with which they're seen in the courseware. Parents are ordered before children.
    Returns:
        children: list of children usage keys for given parent block usage key
    """
    children = course_ordered[parent].get('children', [])
    return children


def _get_children_from_list(parents_list, course_ordered):
    """
    Method for getting children from course structure objects list

    Args:
        parent_list: list of usage keys of course structure elements (e.g. module_state_key s), for example:
        [u'block-v1:edX+DemoX+Demo_Course+type@vertical+block@4e592689563243c484af947465eaef0d']
        course_ordered: (OrderedDict) the blocks of course structure object in the order with which they're seen in the courseware. Parents are ordered before children.
    Returns:
        children: list of child usage keys for given list of parent blocks usage keys
    """
    children_list = []

    for parent in parents_list:
        one_parent_children = _get_children(parent, course_ordered)
        children_list.extend(one_parent_children)

    return children_list


def _get_last_visit(db_query, course_ordered):
    """
    Returns last visited unit

    Args:
        db_query: StudentModule query, filtered by current course_id and enrolled student_id
    Returns:
        last_visit: name of last visited unit for given student in given course
    """
    last_visit_id = db_query.all().order_by('-modified').values_list('module_state_key', flat=True)[:1]

    try:
        block_type = course_ordered[last_visit_id[0]].get('block_type')
        if block_type not in ['course', 'chapter', 'sequential']:
            last_visit = course_ordered[last_visit_id[0]].get('display_name')
        else:
            last_visit_seq = db_query.order_by('-modified').filter(module_type='sequential').values_list('state', flat=True)[:1]
            last_visit_seq_id = db_query.order_by('-modified').filter(module_type='sequential').values_list('module_state_key', flat=True)[:1]
            seq_position = json.loads(last_visit_seq[0]).get('position') - 1
            last_visited_unit = _get_children(last_visit_seq_id[0], course_ordered)[seq_position]
            last_visit = course_ordered[last_visited_unit].get('display_name')

    except Exception:
        last_visit = 'New to course'

    return last_visit


def _get_user_enrollments_with_org_filter(user):
    """
    Returns all user enrollments

    Remove current site orgs from the "filter out" list, if applicable.
    We want to filter and only show enrollments for courses within
    the organizations defined in configuration for the current site.

    Args:
        user - User object, enrolled to current course
    Returns:
        enroll_names: string of comma separeted courses names current user enrolled in
    """
    org_filter_out_set = configuration_helpers.get_all_orgs()
    course_org_filter = configuration_helpers.get_current_site_orgs()

    if course_org_filter:
        org_filter_out_set = org_filter_out_set - set(course_org_filter)

    enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set))
    enroll_keys = [enrollment.course_id for enrollment in enrollments]
    enroll_names = []
    for enroll_key in enroll_keys:
        enroll_name = CourseOverview.objects.filter(id=enroll_key).values_list('display_name', flat=True)[0]
        enroll_names.append(enroll_name)

    return '; '.join(enroll_names)


def _get_status(unit, visited_in_course, sequential, vertical, course_ordered, seq_positions):
    """
    Checks whether user visited course unit or not

    Requires triple-nested for-cicle (sequentials=>verticals=>units)

    Args:
        unit: usage key for vertical child.
        vertical: usage key for sequential child.
        sequential: usage key for sequential (chapter child).
        course_ordered: (OrderedDict) the blocks of course structure object in the order with which they're seen in the     courseware. Parents are ordered before children.
        visited_in_course: list of module_state_key 's (same as usageKey 's) from StudentModule model.
        seq_positions: dictionary with sequential usageKey as key and position as value. Position points to index in        list of sequential children.

    Returns:
        '+': if unit usage key exist in visited_in_course or current vertical index < position of current            sequential.
        '-': else.
    """
    if course_ordered[unit]['block_type'] in ['video', 'problem']:
        if unit in visited_in_course:
            return '+'
        else:
            return '-'

    else:
        current_seq_children_list = _get_children(sequential, course_ordered)
        vert_position_in_seq = current_seq_children_list.index(vertical)
        try:
            last_visit_in_seq_position = seq_positions[sequential]
            if (vert_position_in_seq < last_visit_in_seq_position):
                return '+'
            else:
                return '-'
        except Exception:
            return '-'


def get_report_data_for_course_users(courses, course_id):
    """
    Collects data for csv report with list of course users.

    Args:
        course_id: request.POST.get('course_id', '').strip()
        courses: iterable list of courses from modulestore (xmodule.modulestore.django)

    Returns:
        course_users: dictionary {'header':header, 'data':data}
    """
    try:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    except:
        log.info('Cannot find course %s', course_id)
        return None

    course = _find_course(course_key, courses)
    # for localizing report timezone
    activate('Europe/Kiev')

    if course is None:
        log.info('Cannot find course %s', course_id)
        return None

    data = []
    enrolled_students = User.objects.filter(
        courseenrollment__course_id=course_key)

    # returns a list of chapters (ids)
    # for parsing children (sequentials) in course tree
    course_chapters = get_course_chapters(course_key)

    course_obj = CourseStructure.objects.get(course_id=course_key)  # course content tree, serialised

    # deserialising and converting to OrderedDict with the blocks
    # in the order that they appear in the course
    course_ordered = course_obj.ordered_blocks  # OrderedDict
    # getting list of all sequentials (child for chapter) -
    # The subsections defined in the course outline:
    sequentials = _get_children_from_list(course_chapters, course_ordered)
    # getting list of all verticals (child for sequential) -
    # The units defined in the course outline:
    verticals = _get_children_from_list(sequentials, course_ordered)
    # getting vertical (unit) names
    unit_names = [course_ordered[v].get('display_name') for v in verticals]

    header = ['username', 'email', 'registration date', 'enrolled courses', 'last login', 'last visit', ]

    # preparing list for counting visits for course units (last row in the table)
    visit_count = ['', '', '', '', '', 'Visits:', ]

    for name in unit_names:
        header.append(name)  # adding unit names to the table header
        visit_count.append(0)  # and initiation of status counter

    for u in enrolled_students:  # u - User object, enrolled to current course

        db_query = models.StudentModule.objects.filter(
            course_id__exact=course_key,
            student_id=u.id
        )   # querySet StudentModule
        last_visit = _get_last_visit(db_query, course_ordered)
        # usageKeys for course parts where student have been
        visited_in_course = [b['module_state_key'] for b in db_query.all().values('module_state_key')]
        # getting other student enrollments
        enroll_names = _get_user_enrollments_with_org_filter(u)
        # Comparing course structure chunks (problem, video, html) with units visited in course
        # Need to get positions for sequentials because this is the
        # only one method to check whether student visited html-only lesson or no
        seq_positions = {}  # getting positions for sequential module_types
        visited_in_seq = db_query.filter(module_type='sequential')
        for v in visited_in_seq.values('module_state_key', 'state'):
            # structure example: v = {
            # 'module_state_key': u'block-v1:edX+DemoX+Demo_Course+type@sequential+block@edx_introduction',
            # 'state': u'{"position": 1}'
            # }
            try:
                key = v['module_state_key']
                val = json.loads(v['state']).get('position', '')
                seq_positions[key] = val
            except Exception:
                seq_positions = {}  # it will be replaced with correct exception return

        status_list = []
        # Need to go through parent-children structure again for catching html-only lessons
        for sequential in sequentials:
            for vertical in _get_children(sequential, course_ordered):
                for unit in _get_children(vertical, course_ordered):
                    status = _get_status(unit, visited_in_course, sequential, vertical, course_ordered, seq_positions)
                    if status == '+':
                        break
                status_list.append(status)
        # some default users could be without last_login, so:
        if u.last_login is None:
            last_login = '-'
        else:
            last_login = localtime(u.last_login).strftime('%Y-%m-%d %H:%M')

        d = [
            u.profile.name, u.email, localtime(u.date_joined).strftime('%Y-%m-%d %H:%M'), enroll_names, last_login, last_visit,
        ] + status_list
        data.append(d)
        # Counting visits for every course lesson (vertical)
        index = 6
        for stat in status_list:
            if stat == '+':
                visit_count[index] += 1
                index += 1
            else:
                index += 1
                continue

    data.append(visit_count)

    course_users = {
        'header': header,
        'data': data,
    }
    deactivate()
    return course_users
