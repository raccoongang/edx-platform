from celery.task import task

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
