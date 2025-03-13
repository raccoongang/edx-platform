import logging
from django.contrib.auth import get_user_model
from django.db import models

from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2
from openedx.core.djangoapps.content_libraries import api as contentlib_api

from openedx_learning.apps.authoring.components.models import ComponentVersion

from xblock.core import XBlock
from xmodule.modulestore.django import modulestore
from model_utils.models import TimeStampedModel

log = logging.getLogger(__name__)
User = get_user_model()


def get_course_structure(course_id):
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)

    return get_block_descendants(course)


def get_block_descendants(block: XBlock) -> dict:
    """
    Provides block descendants.
    """
    return {
        str(child.location): get_block_descendants(child)
        for child in block.get_children()
    }


class CourseToLibraryImport(TimeStampedModel):
    """
    Represents a course import into a content library.
    """

    # TODO: move this to data.py as a choice class
    PENDING = 'PENDING'
    READY = 'READY'
    IMPORTED = 'IMPORTED'
    ERROR = 'ERROR'

    IMPORT_STATUSES = (
        (PENDING, 'Pending'),
        (READY, 'Ready'),
        (IMPORTED, 'Imported'),
        (ERROR, 'Error'),
    )

    date = models.DateField(auto_now_add=True)
    state = models.CharField(max_length=100)  # TODO: delete this field
    status = models.CharField(max_length=100, choices=IMPORT_STATUSES, default=PENDING)
    course_ids = models.TextField(
        blank=False,
        help_text="Whitespace-separated list of course keys for which to compute grades."
    )
    library_key = models.CharField(max_length=100)
    source_type = models.CharField(max_length=30)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_ids} - {self.library_key}"

    class Meta:
        verbose_name = 'Course to Library Import'
        verbose_name_plural = 'Course to Library Imports'



class ComponentVersionImport(TimeStampedModel):
    """
    Represents a component version that has been imported into a content library.


    """

    component_version = models.OneToOneField(ComponentVersion, on_delete=models.CASCADE)
    source_usage_key = UsageKeyField(max_length=255)
    library_import = models.ForeignKey(CourseToLibraryImport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.component_version} - {self.source_usage_key}"
