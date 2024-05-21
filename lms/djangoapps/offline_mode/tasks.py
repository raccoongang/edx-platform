from celery import shared_task
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore
from .utils.xblock_helpers import (
    generate_offline_content,
    xblock_view_handler,
    generate_request_with_service_user,
    is_offline_supported,
)


@shared_task
def generate_course_media(course_id):
    request = generate_request_with_service_user()
    course_key = CourseKey.from_string(course_id)
    for xblock in modulestore().get_items(course_key, qualifiers={'category': 'problem'}):
        if is_offline_supported(xblock):
            continue
        html_data = xblock_view_handler(request, xblock)
        generate_offline_content(xblock, html_data)
