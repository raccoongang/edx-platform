"""
Tasks for offline mode feature.
"""
from celery import shared_task
from edx_django_utils.monitoring import set_code_owner_attribute
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore

from .constants import OFFLINE_SUPPORTED_XBLOCKS
from .renderer import XBlockRenderer
from .utils import generate_offline_content, is_offline_supported_block


@shared_task
@set_code_owner_attribute
def generate_offline_content_for_course(course_id):
    """
    Generates offline content for all supported XBlocks in the course.
    """
    course_key = CourseKey.from_string(course_id)
    for xblock in modulestore().get_items(course_key, qualifiers={'category': OFFLINE_SUPPORTED_XBLOCKS}):
        if is_offline_supported_block(xblock):
            html_data = XBlockRenderer(str(xblock.id)).render_xblock_from_lms()
            generate_offline_content(xblock, html_data)
