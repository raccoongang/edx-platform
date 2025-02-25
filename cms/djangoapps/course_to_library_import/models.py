import logging
from django.db import models

from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import LibraryLocatorV2
from openedx.core.djangoapps.content_libraries import api as contentlib_api


log = logging.getLogger(__name__)



from opaque_keys.edx.keys import CourseKey
from xblock.core import XBlock

from xmodule.modulestore.django import modulestore


def get_course_structure(course_id):
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)

    return get_block_descendants(course)


def get_block_descendants(block: XBlock) -> dict:
    """
    Provides block descendants.
    """
    descendants = []

    return {
        str(child.location): get_block_descendants(child)
        for child in block.get_children()
    }




class CourseToLibraryImport(models.Model):
    date = models.DateField(auto_now_add=True)
    state = models.CharField(max_length=100)
    course_id = models.CharField(max_length=100)
    library_key = models.CharField(max_length=100)
    source_type = models.CharField(max_length=30)
    metadata = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        metadata = get_course_structure(self.course_id)
        self.metadata = metadata
        super().save(*args, **kwargs)

        openedx_client = contentlib_api.EdxModulestoreImportClient(
            library_key=LibraryLocatorV2.from_string(self.library_key),
        )

        failed_blocks = []

        def _on_progress(block_key, block_num, block_count, exception=None):
            if exception:
                log.error('Failed to import block: %s', block_key, exc_info=exception)
                failed_blocks.append(block_key)
            else:
                log.info('Block imported: %s', block_key)

        openedx_client.import_blocks_from_course(
            CourseKey.from_string(self.course_id),
            _on_progress
        )
