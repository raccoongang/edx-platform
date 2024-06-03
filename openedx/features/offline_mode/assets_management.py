import shutil
import os
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError

# from .file_management import get_static_file_path, read_static_file


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

        # Define the paths to the specific items to delete
        asset_path = os.path.join(base_path, 'asset')
        index_file_path = os.path.join(base_path, 'index.html')
        # FIXME: change filename to block_id or move to constants
        offline_zip_path = os.path.join(base_path, 'offline_content.zip')

        # Delete the 'asset' directory if it exists
        if os.path.isdir(asset_path):
            shutil.rmtree(asset_path)
            log.info(f"Successfully deleted the directory: {asset_path}")

        # Delete the 'index.html' file if it exists
        if os.path.isfile(index_file_path):
            os.remove(index_file_path)
            log.info(f"Successfully deleted the file: {index_file_path}")

        # Delete the 'offline_content.zip' file if it exists
        if os.path.isfile(offline_zip_path):
            os.remove(offline_zip_path)
            log.info(f"Successfully deleted the file: {offline_zip_path}")

    except Exception as e:
        log.error(f"Error occurred while deleting the files or directory: {e}")


def is_offline_content_present(xblock):
    """
    Checks whether 'offline_content.zip' file is present in the specified base path directory.
    Args:
        xblock (XBlock): The XBlock instance
    Returns:
        bool: True if the file is present, False otherwise
    """
    try:
        base_path = base_storage_path(xblock)
        # FIXME: change filename to block_id or move to constants
        # Define the path to the 'offline_content.zip' file
        offline_zip_path = os.path.join(base_path, 'offline_content.zip')

        # Check if the file exists
        if os.path.isfile(offline_zip_path):
            return True
        else:
            return False

    except Exception as e:
        log.error(f"Error occurred while checking the file: {e}")
        return False


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
    # FIXME: change to os.path.join?
    loc = xblock.location
    return f'{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}/'


def is_modified(xblock):
    """
    Check if the xblock has been modified since the last time the offline content was generated.
    :param xblock:
    :return:
    """
    file_path = os.path.join(base_storage_path(xblock), 'content_html.zip')
    # file_path = f'{base_storage_path(xblock)}content_html.zip'  # FIXME: change filename, and change to os.path.join
    #
    try:
        last_modified = default_storage.get_created_time(file_path)
    except OSError:
        return True

    return xblock.published_on > last_modified
