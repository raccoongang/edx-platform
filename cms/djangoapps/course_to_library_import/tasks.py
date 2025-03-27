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
from xmodule.modulestore.django import modulestore

from .data import CourseToLibraryImportStatus
from .helpers import delete_old_ready_staged_content_by_user_and_purpose, get_block_to_import, import_container
from .models import CourseToLibraryImport
from .types import CompositionLevel
from .validators import validate_composition_level, validate_usage_ids

log = get_task_logger(__name__)


@shared_task
@set_code_owner_attribute
def save_courses_to_staged_content_task(
    course_ids: list[str],
    user_id: int,
    import_task_id,
    purpose: str,
    version_num: int | None = None,
) -> None:
    """
    Save courses to staged content task.
    """
    course_to_library_import = CourseToLibraryImport.get_by_id(import_task_id)
    if not course_to_library_import:
        return

    with transaction.atomic():
        for course_id in course_ids:
            course_key = CourseKey.from_string(course_id)
            sections = modulestore().get_items(
                course_key, qualifiers={"category": "chapter"}
            ) or []
            static_tabs = modulestore().get_items(
                course_key, qualifiers={"category": "static_tab"}
            ) or []

            delete_old_ready_staged_content_by_user_and_purpose(user_id, purpose.format(course_id=course_id))
            for item in sections + static_tabs:
                content_staging_api.stage_xblock_temporarily(
                    item,
                    user_id,
                    purpose=purpose.format(course_id=course_id),
                    version_num=version_num,
                )

        course_to_library_import.status = CourseToLibraryImportStatus.READY
        course_to_library_import.save()


@shared_task
@set_code_owner_attribute
def import_course_staged_content_to_library_task(
    user_id: int,
    usage_ids: list[str],
    library_key: str,
    purpose: str,
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

    staged_content_purposes = [
        purpose.format(course_id=course_id)
        for course_id in course_to_library_import.course_id_list
    ]
    staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
        user_id,
        staged_content_purposes
    )
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
