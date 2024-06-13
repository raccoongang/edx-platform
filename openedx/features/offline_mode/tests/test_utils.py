"""
Tests for the testing Offline Mode utils.
"""

from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

from openedx.features.offline_mode.utils import (
    add_files_to_zip_recursively,
    create_zip_file,
    generate_offline_content,
    save_xblock_html,
)


class OfflineModeUtilsTestCase(TestCase):
    """
    Test case for the testing Offline Mode utils.
    """

    @patch('openedx.features.offline_mode.utils.shutil.rmtree')
    @patch('openedx.features.offline_mode.utils.create_zip_file')
    @patch('openedx.features.offline_mode.utils.save_xblock_html')
    @patch('openedx.features.offline_mode.utils.mkdtemp')
    @patch('openedx.features.offline_mode.utils.remove_old_files')
    @patch('openedx.features.offline_mode.utils.block_storage_path')
    @patch('openedx.features.offline_mode.utils.is_modified')
    def test_generate_offline_content_for_modified_xblock(
        self,
        is_modified_mock: MagicMock,
        block_storage_path_mock: MagicMock,
        remove_old_files_mock: MagicMock,
        mkdtemp_mock: MagicMock,
        save_xblock_html_mock: MagicMock,
        create_zip_file_mock: MagicMock,
        shutil_rmtree_mock: MagicMock,
    ) -> None:
        xblock_mock = Mock()
        html_data_mock = 'html_markup_data_mock'

        generate_offline_content(xblock_mock, html_data_mock)

        is_modified_mock.assert_called_once_with(xblock_mock)
        block_storage_path_mock.assert_called_once_with(xblock_mock)
        remove_old_files_mock.assert_called_once_with(xblock_mock)
        mkdtemp_mock.assert_called_once_with()
        save_xblock_html_mock.assert_called_once_with(mkdtemp_mock.return_value, xblock_mock, html_data_mock)
        create_zip_file_mock.assert_called_once_with(
            mkdtemp_mock.return_value,
            block_storage_path_mock.return_value,
            f'{xblock_mock.location.block_id}.zip'
        )
        shutil_rmtree_mock.assert_called_once_with(mkdtemp_mock.return_value, ignore_errors=True)

    @patch('openedx.features.offline_mode.utils.shutil.rmtree')
    @patch('openedx.features.offline_mode.utils.create_zip_file')
    @patch('openedx.features.offline_mode.utils.save_xblock_html')
    @patch('openedx.features.offline_mode.utils.mkdtemp')
    @patch('openedx.features.offline_mode.utils.remove_old_files')
    @patch('openedx.features.offline_mode.utils.block_storage_path')
    @patch('openedx.features.offline_mode.utils.is_modified', return_value=False)
    def test_generate_offline_content_is_not_modified(
        self,
        is_modified_mock: MagicMock,
        block_storage_path_mock: MagicMock,
        remove_old_files_mock: MagicMock,
        mkdtemp_mock: MagicMock,
        save_xblock_html_mock: MagicMock,
        create_zip_file_mock: MagicMock,
        shutil_rmtree_mock: MagicMock,
    ) -> None:
        xblock_mock = Mock()
        html_data_mock = 'html_markup_data_mock'

        generate_offline_content(xblock_mock, html_data_mock)

        is_modified_mock.assert_called_once_with(xblock_mock)
        block_storage_path_mock.assert_not_called()
        remove_old_files_mock.assert_not_called()
        mkdtemp_mock.assert_not_called()
        save_xblock_html_mock.assert_not_called()
        create_zip_file_mock.assert_not_called()
        shutil_rmtree_mock.assert_not_called()

    @patch('openedx.features.offline_mode.utils.os.path.join')
    @patch('openedx.features.offline_mode.utils.open')
    @patch('openedx.features.offline_mode.utils.HtmlManipulator')
    def test_save_xblock_html(
        self,
        html_manipulator_mock: MagicMock,
        context_manager_mock: MagicMock,
        os_path_join_mock: MagicMock,
    ) -> None:
        tmp_dir_mock = Mock()
        xblock_mock = Mock()
        html_data_mock = 'html_markup_data_mock'

        save_xblock_html(tmp_dir_mock, xblock_mock, html_data_mock)

        html_manipulator_mock.assert_called_once_with(xblock_mock, html_data_mock, tmp_dir_mock)
        html_manipulator_mock.return_value.process_html.assert_called_once_with()
        context_manager_mock.assert_called_once_with(os_path_join_mock.return_value, 'w')
        os_path_join_mock.assert_called_once_with(tmp_dir_mock, 'index.html')
        context_manager_mock.return_value.__enter__.return_value.write.assert_called_once_with(
            html_manipulator_mock.return_value.process_html.return_value
        )

    @patch('openedx.features.offline_mode.utils.log.info')
    @patch('openedx.features.offline_mode.utils.add_files_to_zip_recursively')
    @patch('openedx.features.offline_mode.utils.ZipFile')
    @patch('openedx.features.offline_mode.utils.default_storage')
    @patch('openedx.features.offline_mode.utils.os')
    def test_create_zip_file_os_path_exists(
        self,
        os_mock: MagicMock,
        default_storage_mock: MagicMock,
        zip_file_context_manager: MagicMock,
        add_files_to_zip_recursively_mock: MagicMock,
        log_info_mock: MagicMock,
    ) -> None:
        temp_dir_mock = 'temp_dir_mock'
        base_path_mock = 'base_path_mock'
        file_name_mock = 'file_name_mock'

        create_zip_file(temp_dir_mock, base_path_mock, file_name_mock)

        os_mock.path.exists.assert_called_once_with(default_storage_mock.path.return_value)
        os_mock.makedirs.assert_not_called()
        self.assertListEqual(
            default_storage_mock.path.call_args_list,
            [call(base_path_mock), call(base_path_mock + file_name_mock)]
        )
        zip_file_context_manager.assert_called_once_with(default_storage_mock.path.return_value, 'w')
        zip_file_context_manager.return_value.__enter__.return_value.write.assert_called_once_with(
            os_mock.path.join.return_value, 'index.html'
        )
        add_files_to_zip_recursively_mock.assert_called_once_with(
            zip_file_context_manager.return_value.__enter__.return_value,
            current_base_path=os_mock.path.join.return_value,
            current_path_in_zip='assets',
        )
        log_info_mock.assert_called_once_with(
            f'Offline content for {file_name_mock} has been generated.'
        )

    @patch('openedx.features.offline_mode.utils.log.info')
    @patch('openedx.features.offline_mode.utils.add_files_to_zip_recursively')
    @patch('openedx.features.offline_mode.utils.ZipFile')
    @patch('openedx.features.offline_mode.utils.default_storage')
    @patch('openedx.features.offline_mode.utils.os')
    def test_create_zip_file_os_path_does_not_exists(
        self,
        os_mock: MagicMock,
        default_storage_mock: MagicMock,
        zip_file_context_manager: MagicMock,
        add_files_to_zip_recursively_mock: MagicMock,
        log_info_mock: MagicMock,
    ) -> None:
        temp_dir_mock = 'temp_dir_mock'
        base_path_mock = 'base_path_mock'
        file_name_mock = 'file_name_mock'
        os_mock.path.exists.return_value = False

        create_zip_file(temp_dir_mock, base_path_mock, file_name_mock)

        os_mock.path.exists.assert_called_once_with(default_storage_mock.path.return_value)
        os_mock.makedirs.assert_called_once_with(default_storage_mock.path.return_value)
        self.assertListEqual(
            default_storage_mock.path.call_args_list,
            [call(base_path_mock), call(base_path_mock), call(base_path_mock + file_name_mock)]
        )
        zip_file_context_manager.assert_called_once_with(default_storage_mock.path.return_value, 'w')
        zip_file_context_manager.return_value.__enter__.return_value.write.assert_called_once_with(
            os_mock.path.join.return_value, 'index.html'
        )
        add_files_to_zip_recursively_mock.assert_called_once_with(
            zip_file_context_manager.return_value.__enter__.return_value,
            current_base_path=os_mock.path.join.return_value,
            current_path_in_zip='assets',
        )
        log_info_mock.assert_called_once_with(
            f'Offline content for {file_name_mock} has been generated.'
        )

    @patch('openedx.features.offline_mode.utils.os')
    def test_add_files_to_zip_recursively_successfully_for_file(
        self,
        os_mock: MagicMock,
    ):
        zip_file_mock = Mock()
        current_base_path_mock = 'current_base_path_mock'
        current_path_in_zip_mock = 'current_path_in_zip_mock'
        resource_path_mock = 'resource_path_mock'
        os_mock.listdir.return_value = [resource_path_mock]

        expected_os_mock_path_join_calls = [
            call(current_base_path_mock, resource_path_mock),
            call(current_path_in_zip_mock, resource_path_mock)
        ]

        add_files_to_zip_recursively(zip_file_mock, current_base_path_mock, current_path_in_zip_mock)

        os_mock.listdir.assert_called_once_with(current_base_path_mock)
        self.assertListEqual(os_mock.path.join.call_args_list, expected_os_mock_path_join_calls)
        zip_file_mock.write.assert_called_once_with(os_mock.path.join.return_value, os_mock.path.join.return_value)

    @patch('openedx.features.offline_mode.utils.add_files_to_zip_recursively')
    @patch('openedx.features.offline_mode.utils.os')
    def test_add_files_to_zip_recursively_successfully_recursively_path(
        self,
        os_mock: MagicMock,
        add_files_to_zip_recursively_mock: MagicMock,
    ):
        zip_file_mock = Mock()
        current_base_path_mock = 'current_base_path_mock'
        current_path_in_zip_mock = 'current_path_in_zip_mock'
        resource_path_mock = 'resource_path_mock'
        os_mock.listdir.return_value = [resource_path_mock]
        os_mock.path.isfile.return_value = False

        expected_os_mock_path_join_calls = [
            call(current_base_path_mock, resource_path_mock),
            call(current_path_in_zip_mock, resource_path_mock)
        ]

        add_files_to_zip_recursively(zip_file_mock, current_base_path_mock, current_path_in_zip_mock)

        os_mock.listdir.assert_called_once_with(current_base_path_mock)
        self.assertListEqual(os_mock.path.join.call_args_list, expected_os_mock_path_join_calls)
        add_files_to_zip_recursively_mock.assert_called_once_with(
            zip_file_mock, os_mock.path.join.return_value, os_mock.path.join.return_value
        )

    @patch('openedx.features.offline_mode.utils.log.error')
    @patch('openedx.features.offline_mode.utils.os.listdir', side_effect=OSError)
    def test_add_files_to_zip_recursively_with_os_error(
        self,
        os_mock: MagicMock,
        log_error_mock: MagicMock,
    ):
        zip_file_mock = Mock()
        current_base_path_mock = 'current_base_path_mock'
        current_path_in_zip_mock = 'current_path_in_zip_mock'

        add_files_to_zip_recursively(zip_file_mock, current_base_path_mock, current_path_in_zip_mock)

        os_mock.assert_called_once_with(current_base_path_mock)
        log_error_mock.assert_called_once_with(f'Error while reading the directory: {current_base_path_mock}')
