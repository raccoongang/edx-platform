import unittest
from unittest.mock import Mock, patch, call
import zipfile

from lms.djangoapps.offline_mode.utils.zip_management import create_zip_file


class CreateZipFileTest(unittest.TestCase):

    @patch('your_module.default_storage')
    @patch('your_module.zipfile.ZipFile')
    def test_create_zip_file(self, mock_zipfile, mock_default_storage):
        # Setup mock paths
        base_path = 'test_base_path/'
        file_name = 'test_file.zip'
        index_html_path = f'{base_path}index.html'
        assets_path = f'{base_path}assets/'
        asset_file_path = f'{assets_path}test_asset.txt'

        # Mock default_storage behavior
        mock_default_storage.path.side_effect = lambda x: x
        mock_default_storage.listdir.side_effect = [
            (['assets'], ['index.html']),  # Root directory
            ([], ['test_asset.txt'])       # Assets directory
        ]

        # Mock zipfile behavior
        mock_zf_instance = Mock()
        mock_zipfile.return_value = mock_zf_instance

        # Call the function to test
        create_zip_file(base_path, file_name)

        # Assertions
        mock_zipfile.assert_called_once_with(f'{base_path}{file_name}', 'w')
        mock_zf_instance.write.assert_any_call(index_html_path, 'index.html')
        mock_zf_instance.write.assert_any_call(asset_file_path, 'assets/test_asset.txt')
        mock_zf_instance.close.assert_called_once()

        expected_calls = [
            call(path=f'{base_path}index.html'),
            call(path=f'{assets_path}'),
        ]
        self.assertEqual(mock_default_storage.path.call_count, 2)
        mock_default_storage.path.assert_has_calls(expected_calls, any_order=True)
