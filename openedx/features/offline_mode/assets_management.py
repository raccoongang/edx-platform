"""
This module contains utility functions for managing assets and files.
"""
import shutil
import logging
import os
import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError

from .constants import MATHJAX_CDN_URL, MATHJAX_STATIC_PATH, OFFLINE_CONTENT_ARCHIVE_NAME


log = logging.getLogger(__name__)


def get_static_file_path(relative_path):
    """
    Constructs the absolute path for a static file based on its relative path.
    """
    base_path = settings.STATIC_ROOT
    return os.path.join(base_path, relative_path)


def read_static_file(path):
    """
    Reads the contents of a static file in binary mode.
    """
    with open(path, 'rb') as file:
        return file.read()


def save_asset_file(xblock, path, filename):
    """
    Saves an asset file to the default storage.

    If the filename contains a '/', it reads the static file directly from the file system.
    Otherwise, it fetches the asset from the AssetManager.
    Args:
        xblock (XBlock): The XBlock instance
        path (str): The path where the asset is located.
        filename (str): The name of the file to be saved.
    """
    try:
        if '/' in filename:
            static_path = get_static_file_path(filename)
            content = read_static_file(static_path)
        else:
            asset_key = StaticContent.get_asset_key_from_path(xblock.location.course_key, path)
            content = AssetManager.find(asset_key).data
    except (ItemNotFoundError, NotFoundError):
        pass
    else:
        base_path = base_storage_path(xblock)
        file_path = os.path.join(base_path, 'assets', filename)
        default_storage.save(file_path, ContentFile(content))


def remove_old_files(xblock):
    """
    Removes the 'asset' directory, 'index.html', and 'offline_content.zip' files
    in the specified base path directory.
    Args:
        (XBlock): The XBlock instance
    """
    try:
        base_path = base_storage_path(xblock)
        asset_path = os.path.join(base_path, 'asset')
        index_file_path = os.path.join(base_path, 'index.html')
        offline_zip_path = os.path.join(base_path, OFFLINE_CONTENT_ARCHIVE_NAME)

        # Delete the 'asset' directory if it exists
        if os.path.isdir(asset_path):
            shutil.rmtree(asset_path)
            log.info(f"Successfully deleted the directory: {asset_path}")

        # Delete the 'index.html' file if it exists
        if default_storage.exists(index_file_path):
            os.remove(index_file_path)
            log.info(f"Successfully deleted the file: {index_file_path}")

        # Delete the 'offline_content.zip' file if it exists
        if default_storage.exists(offline_zip_path):
            os.remove(offline_zip_path)
            log.info(f"Successfully deleted the file: {offline_zip_path}")

    except OSError as e:
        log.error(f"Error occurred while deleting the files or directory: {e}")


def is_offline_content_present(xblock):
    """
    Checks whether 'offline_content.zip' file is present in the specified base path directory.

    Args:
        xblock (XBlock): The XBlock instance
    Returns:
        bool: True if the file is present, False otherwise
    """
    base_path = base_storage_path(xblock)
    offline_zip_path = os.path.join(base_path, OFFLINE_CONTENT_ARCHIVE_NAME)
    return default_storage.exists(offline_zip_path)


def base_storage_path(xblock):
    """
    Generates the base storage path for the given XBlock.

    The path is constructed based on the XBlock's location, which includes the organization,
    course, block type, and block ID.
    Args:
        xblock (XBlock): The XBlock instance for which to generate the storage path.
    Returns:
        str: The constructed base storage path.
    """
    loc = xblock.location
    return f'{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}/'


def is_modified(xblock):
    """
    Check if the xblock has been modified since the last time the offline content was generated.

    Args:
        xblock (XBlock): The XBlock instance to check.
    """
    file_path = os.path.join(base_storage_path(xblock), 'content_html.zip')

    try:
        last_modified = default_storage.get_created_time(file_path)
    except OSError:
        return True

    return xblock.published_on > last_modified


def save_mathjax_to_local_static():
    """
    Saves MathJax to the local static directory.

    If MathJax is not already saved, it fetches MathJax from
    the CDN and saves it to the local static directory.
    """
    if not default_storage.exists(MATHJAX_STATIC_PATH):
        response = requests.get(MATHJAX_CDN_URL)
        default_storage.save(MATHJAX_STATIC_PATH, ContentFile(response.content))
        log.info(f"Successfully saved MathJax to {MATHJAX_STATIC_PATH}")
