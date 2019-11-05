from celery.task import task
from django.conf import settings
from django.core.urlresolvers import reverse

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


@task
def task_reindex_courses(category_id=None, course_keys=None):
    from course_category.models import CourseCategory
    from cms.djangoapps.contentstore.courseware_index import CoursewareSearchIndexer
    courses = set(course_keys) if course_keys else set()
    if category_id:
        category = CourseCategory.objects.filter(id=category_id).first()
        if category:
            courses.update(category.courses.all().values_list('id', flat=True))
            courses.update(category.get_descendants().values_list('courses', flat=True))

    for course_key in courses:
        course_key = CourseKey.from_string(course_key)
        CoursewareSearchIndexer.do_course_reindex(modulestore(), course_key)


@task
def task_add_categories(category_names, course_id):
    from course_category.models import CourseCategory
    for category_name in category_names:
        category = CourseCategory.objects.filter(name=category_name).first()
        if category:
            category.courses.add(CourseKey.from_string(course_id))


@task
def task_enroll_category(user_id, slug, is_secure):
    """
    Task for enrolling to category courses after pressing "Bulk Enroll" button.

    Args:
        user_id (int) - current user;
        slug (str) - category to enroll slug;
        is_secure (True/False) - request.is_secure()
    """
    # Imports included to task to prevent ImportError.
    from django.contrib.auth import get_user_model

    from course_category.utils import enroll_category, send_email_with_enroll_status
    from .models import CourseCategory

    User = get_user_model()

    user = User.objects.filter(id=user_id).first()
    category = CourseCategory.objects.filter(slug=slug).first()

    enroll_result = enroll_category(user, category)

    enrolled_courses = [
        {'display_name': course.display_name, 'link': get_course_about_link(course.id, is_secure)}
        for course in enroll_result.get('enrolled', [])
    ]

    not_enrolled_courses = [
        {'display_name': course.display_name, 'link': get_course_about_link(course.id, is_secure)}
        for course in enroll_result.get('not_enrolled', [])
    ]

    enroll_info = {
        'enrolled_courses': enrolled_courses,
        'not_enrolled_courses': not_enrolled_courses,
    }

    site_name = settings.SITE_NAME

    send_email_with_enroll_status(site_name, user, category, enroll_info)

def get_course_about_link(course_key, is_secure):
    """
    Constructs the 'about_course' URL.
    """
    about_path = reverse('about_course', kwargs={'course_id': str(course_key)})

    schem = 'https://' if is_secure else 'http://'

    return u'{}{}{}'.format(schem, settings.SITE_NAME, about_path)
