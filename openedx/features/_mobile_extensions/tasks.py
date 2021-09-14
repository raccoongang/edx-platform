from celery.task import task
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore


@task
def update_html_block_mobile_api(course_id):
    course_key = CourseKey.from_string(course_id)

    for xblock_html in modulestore().get_items(course_key, qualifiers={'category': 'html'}):
        xblock_html.update_info_api()
