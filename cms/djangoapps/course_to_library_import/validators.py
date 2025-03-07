"""
Validators for the course_to_library_import app.
"""

from django.utils.translation import gettext_lazy as _
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey


def validate_course_ids(value: str):
    """
    Validate that the course_ids are valid course keys.

    Args:
        value (str): A string containing course IDs separated by spaces.

    Raises:
        ValueError: If any of the course IDs are not valid course keys.
    """

    for course_id in value.split():
        try:
            CourseKey.from_string(course_id)
        except InvalidKeyError as exc:
            raise ValueError(_('Invalid course key: {course_id}').format(course_id=course_id)) from exc
