from celery.task import task

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


@task
def task_reindex_course(course_key):
    from cms.djangoapps.contentstore.courseware_index import CoursewareSearchIndexer
    from course_category.models import CourseCategory
    course_key = CourseKey.from_string(course_key)
    CoursewareSearchIndexer.do_course_reindex(modulestore(), course_key)

@task
def task_reindex_courses(category_id):
    from course_category.models import CourseCategory
    from cms.djangoapps.contentstore.courseware_index import CoursewareSearchIndexer
    for course_key in CourseCategory.objects.get(id=category_id).get_course_ids():
        CoursewareSearchIndexer.do_course_reindex(modulestore(), course_key)
