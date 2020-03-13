from django.apps import apps
from django.core.cache import cache
from opaque_keys.edx.keys import CourseKey

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from lms.djangoapps.hera.mongo import BLOCK_ID, USER, c_user_lesson_coins
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore


CACHING_USER_ACTIVE_COURSE_KEY = 'hera:active_course:{user_id}'
CACHING_TIMEOUT = 60 * 15


def get_lesson_summary_xblock_context(user, course_key, current_unit):
    """
    Get lesson_summary xblock final grades.
    """
    # current import used inside function for correct studio work, studio cannot see hera app templates and models
    from hera.models import MedalsSettings

    course_grade = CourseGradeFactory().read(user, course_key=course_key)
    courseware_summary = course_grade.chapter_grades.values()

    points = 0
    lesson_title = ''

    for subsection in modulestore().get_items(course_key):
        for unit in subsection.get_children():
            if unit.location.block_id == current_unit:
                lesson_title = subsection.display_name
                current_subsection = subsection
                break

    for chapter in courseware_summary:
        if not chapter['display_name'] == "hidden":
            for subsection in chapter['sections']:  # the sections in chapter are actually subsection
                if subsection.location.block_id == current_subsection.location.block_id:
                    try:
                        points = int(subsection.all_total.earned / subsection.all_total.possible * 100)
                    except ZeroDivisionError:
                        points = 0
                    break

    medal, _ = MedalsSettings.get_medal(points)
    return {
        'lesson_title': lesson_title,
        'points': points,
        'medal': medal
    }


def recalculate_coins(course_id, block_id, user_id, cost=0):
    """
    Return difference between the user coins and cost.
    If user has less coins than given cost - return None.
    """
    course = modulestore().get_course(CourseKey.from_string(course_id))
    subsection_id = None
    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                for block in unit.get_children():
                    if block.scope_ids.usage_id.block_id == block_id:
                        subsection_id = subsection.scope_ids.usage_id.block_id
                        break

    user_lesson_coins = c_user_lesson_coins().find_one({
        BLOCK_ID: subsection_id,
        USER: user_id,
    })
    user_coins = user_lesson_coins.get('coins', 0)
    if cost <= user_coins:
        coins_balance = user_coins - cost
        c_user_lesson_coins().update(
            {
                BLOCK_ID: subsection_id,
                USER: user_id,
            },
            {
                '$set': {
                    'coins': coins_balance,
                }
            },
            upsert=True
        )
        return coins_balance
    return None


def get_scaffolds_settings():
    ScaffoldsSettings = apps.get_model('hera', 'ScaffoldsSettings')
    return ScaffoldsSettings.get()


def get_users_last_enroll(user):
    """
    Get the last user enrollment on the Course with existing CourseOverview.
    CourseEnrollments aren't removed when deleting CoourseOverview
    and `enrollments_for_user` returns enrollments even for not existing CourseOverviews.

    """
    user_enrollments = []
    enrollments = CourseEnrollment.enrollments_for_user(user=user)
    for enrollment in enrollments:
        try:
            enrollment.course
        except CourseOverview.DoesNotExist:
            pass
        else:
            user_enrollments.append(enrollment)
    if user_enrollments:
        return user_enrollments[-1]


def get_user_active_course_id(user):
    """
    Returns a cached active course if is.
    """
    cached_course_id = cache.get(
        CACHING_USER_ACTIVE_COURSE_KEY.format(user_id=user.id)
    )
    if cached_course_id:
        return cached_course_id
    else:
        last = get_users_last_enroll(user)
        if last:
            last_course_id = last.course_id
            cache.set(
                CACHING_USER_ACTIVE_COURSE_KEY.format(user_id=user.id),
                last_course_id,
                CACHING_TIMEOUT
            )
            return last_course_id


def clear_active_course_cache(user_id):
    cache.delete(
        CACHING_USER_ACTIVE_COURSE_KEY.format(user_id=user_id)
    )
