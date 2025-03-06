""""
Python API for course to library import
=======================================
"""
import logging
import mimetypes
from collections import ChainMap
from datetime import datetime, timezone

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from lxml import etree

from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2
from openedx_events.content_authoring.signals import LIBRARY_BLOCK_CREATED
from openedx_events.content_authoring.data import LibraryBlockData
from openedx_learning.api import authoring as authoring_api

from openedx.core.djangoapps.content_libraries import api, permissions
from openedx.core.djangoapps.content_staging import api as content_staging_api
from openedx.core.djangoapps.content_staging.models import StagedContent
from xmodule.modulestore.django import modulestore

from .models import CourseToLibraryImport

log = logging.getLogger(__name__)
COURSE_TO_LIBRARY_IMPORT_PURPOSE = 'course_to_library_import'
User = get_user_model()

def save_course_to_staged_content(course_id, user_id, purpose=None, version_num=None):
    """

    :param user_id:
    :param course_id:
    :param purpose:
    :param version_num:
    :return:
    """
    course_key = CourseKey.from_string(course_id)
    sections = modulestore().get_items(course_key, qualifiers={'category': 'chapter'})
    for section in sections:
        content_staging_api.stage_xblock_temporarily(
            section,
            user_id,
            purpose=purpose or COURSE_TO_LIBRARY_IMPORT_PURPOSE,
            version_num=version_num
        )


def import_library_from_staged_content(library_key, user_id, usage_ids):
    """

    :param library_key:
    :param user_id:
    :param usage_ids:
    :return:\
    """
    # Get staged content with user id status READY and purpose COURSE_TO_LIBRARY_IMPORT_PURPOSE
    # validate usage_ids in staged content tags
    # parse staged content OLX
    # iter for child of section, validate OLX for unit and xblock level
    # import OLX to library q
    # ref import_staged_content_from_user_clipboard,
    # + create ComponentVersionImport objects
    # + update CourseToLibraryImport status to IMPORTED
    # USE TRANSACTION!
    staged_content = StagedContent.objects.filter(
        user_id=user_id,
        status='Ready',
        purpose=COURSE_TO_LIBRARY_IMPORT_PURPOSE,
    )
    validate_usage_ids(usage_ids, staged_content)
    parser = etree.XMLParser(strip_cdata=False)
    library_key = LibraryLocatorV2.from_string(library_key)
    imported = False
    for usage_key in usage_ids:
        if staged_content_item := staged_content.filter(tags__icontains=usage_key).first():
            node = etree.fromstring(staged_content_item.olx, parser=parser)
            usage_key = UsageKey.from_string(usage_key)
            block_to_import = get_block_to_import(node, usage_key)
            if not block_to_import:
                continue
            if block_to_import.tag in ('chapter', 'sequential', 'vertical'):
                # TODO: add support different composition
                flat_import_children(block_to_import, library_key, user_id, staged_content_item.id)
            else:
                # validate_can_add_block_to_library(library_key, block_to_import.tag, block_to_import.get('url_name'))
                create_block_in_library(block_to_import, usage_key, library_key, user_id, staged_content_item.id)
            imported = True

    if imported:
        CourseToLibraryImport.objects.filter(
            user_id=user_id,
            library_key=library_key
        ).update(status=CourseToLibraryImport.IMPORTED)


def flat_import_children(block_to_import, content_library, user_id, staged_content):
    for child in block_to_import.getchildren():
        if child.tag in ('chapter', 'sequential', 'vertical'):
            flat_import_children(child, content_library, user_id, staged_content.id)
        else:
            usage_key_fragment = f"type@{child.tag}+block@{child.get('url_name')}"
            usage_key = None
            for tag_key in staged_content.tags.keys():
                if usage_key_fragment in tag_key:
                    usage_key = UsageKey.from_string(child.get('url_name'))  # FIXME find better way to get usage_key
                    break
            if usage_key:
                create_block_in_library(child, usage_key, content_library, user_id, staged_content.id)


def create_block_in_library(block_to_import, usage_key, library_key, user_id, staged_content_id):

    now = datetime.now(tz=timezone.utc)
    staged_content_files = content_staging_api.get_staged_content_static_files(staged_content_id)
    content_library, library_usage_key = api.validate_can_add_block_to_library(
        library_key,
        block_to_import.tag,
        usage_key.block_id,
    )

    with transaction.atomic():
        component_type = authoring_api.get_or_create_component_type("xblock.v1", usage_key.block_type)
        authoring_api.create_component(
            content_library.learning_package.id,
            component_type=component_type,
            local_key=usage_key.block_id,
            created=now,
            created_by=user_id,
        )
        component_version = api.set_library_block_olx(library_usage_key, etree.tostring(block_to_import))

        for staged_content_file_data in staged_content_files:
            filename = staged_content_file_data.filename
            file_data = content_staging_api.get_staged_content_static_file_data(
                staged_content_id,
                filename,
            )
            if not file_data:
                log.error(
                    f"Staged content {staged_content_id} included referenced "
                    f"file {filename}, but no file data was found."
                )
                continue

            filename = f"static/{str(usage_key)}"

            media_type_str, _encoding = mimetypes.guess_type(filename)
            if not media_type_str:
                media_type_str = "application/octet-stream"

            media_type = authoring_api.get_or_create_media_type(media_type_str)
            content = authoring_api.get_or_create_file_content(
                content_library.learning_package.id,
                media_type.id,
                data=file_data,
                created=now,
            )

            # authoring_api.create_component_version_content(
            #     component_version.pk,
            #     content.id,
            #     key=filename,
            # )

    LIBRARY_BLOCK_CREATED.send_event(
        library_block=LibraryBlockData(
            library_key=content_library.library_key,
            usage_key=usage_key
        )
    )


def get_block_to_import(node, usage_key):
    if node.get('url_name') == usage_key.block_id:
        return node

    for child in node.getchildren():
        if found := get_block_to_import(child, usage_key):
            return found


def validate_usage_ids(usage_ids, staged_content):
    available_block_keys = ChainMap(*staged_content.values_list('tags', flat=True))
    for usage_key in usage_ids:
        if usage_key not in available_block_keys:
            raise ValueError(f'Block {usage_key} is not available for import')


def create_import(course_ids, user_id, library_key, source_type):
    """
    Create a new import task to import a course to a library.

    Args:
        course_ids (str): The course key of the course to import.
        user_id (int): The ID of the user who initiated the import.
        library_key (str): The key of the library to import the course to.
        source_type (str): The type of the source of the import.
    """
    for course_id in course_ids:
        save_course_to_staged_content(course_id, user_id, COURSE_TO_LIBRARY_IMPORT_PURPOSE)

    import_task = CourseToLibraryImport(  # FIXME: args
        course_id=course_ids,
        library_key=library_key,
        source_type=source_type
    )
    import_task.save()

    return import_task


def get_import(import_id):
    """
    Get an import task by its ID.

    Args:
        import_id (int): The ID of the import task to get.

    Returns:
        CourseToLibraryImport: The import task.
    """
    return CourseToLibraryImport.objects.get(id=import_id)


def get_imports():
    """
    Get all import tasks.

    Returns:
        QuerySet: The import tasks.
    """
    return CourseToLibraryImport.objects.all()
