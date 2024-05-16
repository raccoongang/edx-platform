import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError

from .file_management import get_static_file_path, read_static_file


def save_asset_file(xblock, path, filename):
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
        default_storage.save(f'{base_path}assets/{filename}', ContentFile(content))


def remove_old_files(base_path):
    try:
        directories, files = default_storage.listdir(base_path)
    except OSError:
        pass
    else:
        for file_name in files:
            default_storage.delete(base_path + file_name)

    try:
        directories, files = default_storage.listdir(base_path + 'assets/')
    except OSError:
        pass
    else:
        for file_name in files:
            default_storage.delete(base_path + 'assets/' + file_name)


def base_storage_path(xblock):
    return '{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}/'.format(loc=xblock.location)
