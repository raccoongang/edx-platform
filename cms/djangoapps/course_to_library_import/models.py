import logging
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from opaque_keys.edx.django.models import UsageKeyField
from opaque_keys.edx.keys import CourseKey

from openedx_learning.apps.authoring.components.models import ComponentVersion

from xblock.core import XBlock
from xmodule.modulestore.django import modulestore
from model_utils.models import TimeStampedModel

from .data import CourseToLibraryImportStatus
from .validators import validate_course_ids

logger = logging.getLogger(__name__)
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

    status = models.CharField(
        max_length=100,
        choices=CourseToLibraryImportStatus.choices,
        default=CourseToLibraryImportStatus.PENDING
    )
    course_ids = models.TextField(
        blank=False,
        help_text=_("Whitespace-separated list of course keys for which to compute grades."),
        validators=[validate_course_ids]
    )
    library_key = models.CharField(max_length=100)
    source_type = models.CharField(max_length=30)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_ids} - {self.library_key}"

    class Meta:
        verbose_name = _('Course to Library Import')
        verbose_name_plural = _('Course to Library Imports')


class ComponentVersionImport(TimeStampedModel):
    """
    Represents a component version that has been imported into a content library.
    This is a many-to-many relationship between a component version and a course to library import.
    """

    component_version = models.OneToOneField(ComponentVersion, on_delete=models.CASCADE)
    source_usage_key = UsageKeyField(max_length=255)
    library_import = models.ForeignKey(CourseToLibraryImport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.component_version} - {self.source_usage_key}"

    class Meta:
        verbose_name = _('Component Version Import')
        verbose_name_plural = _('Component Version Imports')
