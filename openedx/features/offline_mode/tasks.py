from celery import shared_task
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore

from .renderer import XBlockRenderer
from .utils import generate_offline_content


@shared_task
def get_rendered_xblock_from_lms(course_id):
    course_key = CourseKey.from_string(course_id)
    for xblock in modulestore().get_items(course_key, qualifiers={'category': 'problem'}):
        # if is_offline_supported(xblock):
        #     continue
        html_data = XBlockRenderer(str(xblock.id)).render_xblock_from_lms()
        generate_offline_content(xblock, html_data)
