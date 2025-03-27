"""
Tasks for course to library import.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from edx_django_utils.monitoring import set_code_owner_attribute
from lxml import etree
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2

from openedx.core.djangoapps.content_staging import api as content_staging_api
from openedx.core.djangoapps.content_staging.data import StagedContentStatus
from xmodule.modulestore.django import modulestore

from .constants import COURSE_TO_LIBRARY_IMPORT_PURPOSE
from .data import CourseToLibraryImportStatus
from .helpers import delete_old_ready_staged_content_by_user_and_purpose, get_block_to_import, import_container
from .models import CourseToLibraryImport
from .types import CompositionLevel
from .validators import validate_composition_level, validate_usage_ids

log = get_task_logger(__name__)


@shared_task
@set_code_owner_attribute
def save_courses_to_staged_content_task(user_id: int, import_uuid: str, version_num: int | None = None) -> None:
    """
    Save courses to staged content task.
    """
    course_to_library_import = CourseToLibraryImport.get_by_uuid(import_uuid)
    if not course_to_library_import:
        return

    delete_old_ready_staged_content_by_user_and_purpose(
        course_to_library_import.course_ids,
        course_to_library_import.library_key,
        course_to_library_import.user.id,
    )

    with transaction.atomic():
        for course_id in course_to_library_import.course_id_list:
            course_key = CourseKey.from_string(course_id)
            sections = modulestore().get_items(course_key, qualifiers={"category": "chapter"}) or []
            static_tabs = modulestore().get_items(course_key, qualifiers={"category": "static_tab"}) or []

            for item in sections + static_tabs:
                staged_content = content_staging_api.stage_xblock_temporarily(
                    item,
                    user_id,
                    purpose=COURSE_TO_LIBRARY_IMPORT_PURPOSE,
                    version_num=version_num,
                )
                staged_content.related_import = course_to_library_import
                staged_content.source_course_id = CourseKey.from_string(course_id)
                staged_content.save()

        course_to_library_import.status = CourseToLibraryImportStatus.READY
        course_to_library_import.save()


@shared_task
@set_code_owner_attribute
def import_course_staged_content_to_library_task(
    user_id: int,
    usage_ids: list[str],
    library_key: str,
    import_id: str,
    composition_level: CompositionLevel,
    override: bool
) -> None:
    """
    Import staged content to a library task.
    """
    validate_composition_level(composition_level)
    course_to_library_import = CourseToLibraryImport.get_ready_by_uuid(import_id)
    if not course_to_library_import:
        log.info("Course to library import not found")
        return

    staged_content = course_to_library_import.stagedcontent_set.filter(status=StagedContentStatus.READY)
    validate_usage_ids(usage_ids, staged_content)
    parser = etree.XMLParser(strip_cdata=False)
    library_key = LibraryLocatorV2.from_string(library_key)

    with transaction.atomic():
        for usage_key in usage_ids:
            if staged_content_item := staged_content.filter(tags__icontains=usage_key).first():
                node = etree.fromstring(staged_content_item.olx, parser=parser)
                usage_key = UsageKey.from_string(usage_key)
                block_to_import = get_block_to_import(node, usage_key)

                if block_to_import is None:
                    continue
                import_container(
                    usage_key,
                    block_to_import,
                    library_key,
                    user_id,
                    staged_content_item,
                    composition_level,
                    import_id,
                    override,
                )
        staged_content.delete()

        course_to_library_import.status = CourseToLibraryImportStatus.IMPORTED
        course_to_library_import.save()
