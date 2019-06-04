from celery.task import task

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


@task
def task_reindex_courses(category_id, course_keys=None):
    from course_category.models import CourseCategory
    from cms.djangoapps.contentstore.courseware_index import CoursewareSearchIndexer
    courses = set(course_keys) if course_keys else set()

    if category_id:
        courses.update(CourseCategory.objects.get(id=category_id).courses.all().values_list('id', flat=True))
        courses.update(CourseCategory.objects.get(id=category_id).get_descendants().values_list('courses', flat=True))

    for course_key in courses:
        course_key = CourseKey.from_string(course_key)
        CoursewareSearchIndexer.do_course_reindex(modulestore(), course_key)
