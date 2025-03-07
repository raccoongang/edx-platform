""""
API for course to library import.
"""

from django.contrib.auth import get_user_model

from .tasks import save_course_to_staged_content_task

COURSE_TO_LIBRARY_IMPORT_PURPOSE = 'course_to_library_import'
User = get_user_model()


def save_course_to_staged_content(course_id, user_id, purpose=COURSE_TO_LIBRARY_IMPORT_PURPOSE, version_num=None):
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

    save_course_to_staged_content_task.delay(course_id, user_id, purpose, version_num)
