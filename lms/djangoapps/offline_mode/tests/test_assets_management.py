import os

from unittest import TestCase
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError

from .file_management import save_asset_file, remove_old_files, base_storage_path

class TestFileManagement(TestCase):

    @patch('file_management.get_static_file_path')
    @patch('file_management.read_static_file')
    @patch('xmodule.contentstore.content.StaticContent.get_asset_key_from_path')
    @patch('xmodule.assetstore.assetmgr.AssetManager.find')
    @patch('django.core.files.storage.default_storage.save')
    def test_save_asset_file_with_static_file(
        self,
        mock_save,
        mock_find,
        mock_get_asset_key,
        mock_read_static_file,
        mock_get_static_file_path
    ):
        xblock = MagicMock()
        xblock.location.course_key = 'course-v1:edX+DemoX+Demo_Course'
        path = 'path/to/asset'
        filename = 'static/file/path.txt'
        content = b'some content'

        mock_get_static_file_path.return_value = 'static/file/path.txt'
        mock_read_static_file.return_value = content

        save_asset_file(xblock, path, filename)

        mock_get_static_file_path.assert_called_with(filename)
        mock_read_static_file.assert_called_with('static/file/path.txt')
        mock_save.assert_called_with(
            f'{xblock.location.org}/{xblock.location.course}'
            f'/{xblock.location.block_type}/{xblock.location.block_id}/assets/{filename}',
            ContentFile(content)
        )

    @patch('xmodule.contentstore.content.StaticContent.get_asset_key_from_path')
    @patch('xmodule.assetstore.assetmgr.AssetManager.find')
    @patch('django.core.files.storage.default_storage.save')
    def test_save_asset_file_with_asset_manager(self, mock_save, mock_find, mock_get_asset_key):
        xblock = MagicMock()
        xblock.location.course_key = 'course-v1:edX+DemoX+Demo_Course'
        path = 'path/to/asset'
        filename = 'asset.txt'
        content = b'some content'

        mock_get_asset_key.return_value = 'asset_key'
        mock_find.return_value.data = content

        save_asset_file(xblock, path, filename)

        mock_get_asset_key.assert_called_with(xblock.location.course_key, path)
        mock_find.assert_called_with('asset_key')
        mock_save.assert_called_with(
            f'{xblock.location.org}/{xblock.location.course}'
            f'/{xblock.location.block_type}/{xblock.location.block_id}/assets/{filename}',
            ContentFile(content)
        )

    @patch('xmodule.contentstore.content.StaticContent.get_asset_key_from_path')
    @patch('xmodule.assetstore.assetmgr.AssetManager.find')
    @patch('file_management.get_static_file_path')
    @patch('file_management.read_static_file')
    @patch('django.core.files.storage.default_storage.save')
    def test_save_asset_file_not_found_error(
        self,
        mock_save,
        mock_read_static_file,
        mock_get_static_file_path,
        mock_find,
        mock_get_asset_key
    ):
        xblock = MagicMock()
        xblock.location.course_key = 'course-v1:edX+DemoX+Demo_Course'
        path = 'path/to/asset'
        filename = 'asset.txt'

        mock_get_asset_key.side_effect = ItemNotFoundError
        mock_find.side_effect = NotFoundError

        save_asset_file(xblock, path, filename)

        mock_save.assert_not_called()

    @patch('django.core.files.storage.default_storage.listdir')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_old_files(self, mock_delete, mock_listdir):
        base_path = 'base/path/'
        files = ['file1.txt', 'file2.txt']
        assets_files = ['asset1.txt', 'asset2.txt']

        mock_listdir.side_effect = [
            ([], files),  # for base_path
            ([], assets_files),  # for base_path + 'assets/'
        ]

        remove_old_files(base_path)

        expected_delete_calls = [
            patch('django.core.files.storage.default_storage.delete').call(base_path + 'file1.txt'),
            patch('django.core.files.storage.default_storage.delete').call(base_path + 'file2.txt'),
            patch('django.core.files.storage.default_storage.delete').call(base_path + 'assets/' + 'asset1.txt'),
            patch('django.core.files.storage.default_storage.delete').call(base_path + 'assets/' + 'asset2.txt'),
        ]

        mock_delete.assert_has_calls(expected_delete_calls, any_order=True)

    @patch('django.core.files.storage.default_storage.listdir')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_old_files_os_error(self, mock_delete, mock_listdir):
        base_path = 'base/path/'

        mock_listdir.side_effect = OSError

        remove_old_files(base_path)

        mock_delete.assert_not_called()

    def test_base_storage_path(self):
        xblock = MagicMock()
        xblock.location.org = 'edX'
        xblock.location.course = 'DemoX'
        xblock.location.block_type = 'block'
        xblock.location.block_id = 'block_id'

        expected_path = 'edX/DemoX/block/block_id/'

        self.assertEqual(base_storage_path(xblock), expected_path)
