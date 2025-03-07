"""
Tasks for course to library import.
"""

from celery import shared_task
from edx_django_utils.monitoring import set_code_owner_attribute
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content_staging import api as content_staging_api
from xmodule.modulestore.django import modulestore


@shared_task
@set_code_owner_attribute
def save_course_to_staged_content_task(course_id, user_id, purpose, version_num):
    """
    Save course to staged content.

    Args:
        course_id (str): Course ID.
        user_id (int): User ID.
        purpose (str): Purpose of staging.
        version_num (int): Version number.

    Returns:
        None
    """

    course_key = CourseKey.from_string(course_id)
    sections = modulestore().get_items(course_key, qualifiers={'category': 'chapter'})

    for section in sections:
        content_staging_api.stage_xblock_temporarily(
            section,
            user_id,
            purpose=purpose,
            version_num=version_num,
        )
