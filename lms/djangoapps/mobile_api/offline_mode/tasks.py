from celery import shared_task
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore


@shared_task
def generate_course_media(course_id):
    course_key = CourseKey.from_string(course_id)

    for xblock_html in modulestore().get_items(course_key, qualifiers={'category': ['html', 'problem']}):
        xblock_html.update_info_api()
