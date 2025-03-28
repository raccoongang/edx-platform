"""
Validators for the course_to_library_import app.
"""

from collections import ChainMap
import logging
from typing import get_args

from django.utils.translation import gettext_lazy as _
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from .types import CompositionLevel


log = logging.getLogger(__name__)


def validate_course_ids(value: str):
    """
    Validate that the course_ids are valid course keys.

    Args:
        value (str): A string containing course IDs separated by spaces.

    Raises:
        ValueError: If the course IDs are not valid course keys or if there are duplicate course keys.
    """

    course_ids = value.split()
    if len(course_ids) != len(set(course_ids)):
        raise ValueError(_('Duplicate course keys are not allowed'))

    for course_id in course_ids:
        try:
            CourseKey.from_string(course_id)
        except InvalidKeyError as exc:
            raise ValueError(_('Invalid course key: {course_id}').format(course_id=course_id)) from exc


def validate_usage_ids(usage_ids, staged_content):
    """
    Validate that the usage IDs are valid and available in the staged content.

    Returns:
        list: A list of valid usage IDs.
    """
    valid_usage_ids = []
    available_block_keys = ChainMap(*staged_content.values_list('tags', flat=True))
    for usage_key in usage_ids:
        if usage_key not in available_block_keys:
            log.warning('Block %s is not available for import', usage_key)
        else:
            valid_usage_ids.append(usage_key)
    return valid_usage_ids


def validate_composition_level(composition_level):
    if composition_level not in get_args(CompositionLevel):
        raise ValueError(
            _('Invalid composition level: {composition_level}').format(composition_level=composition_level)
        )
