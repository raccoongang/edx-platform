"""
Tests for the testing methods for prepare HTML content for offline using.
"""

from bs4 import BeautifulSoup
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from openedx.features.offline_mode.constants import MATHJAX_CDN_URL, MATHJAX_STATIC_PATH
from openedx.features.offline_mode.html_manipulator import HtmlManipulator


class HtmlManipulatorTestCase(TestCase):
    """
    Test case for the testing `HtmlManipulator` methods.
    """

    @patch('openedx.features.offline_mode.html_manipulator.HtmlManipulator._replace_iframe')
    @patch('openedx.features.offline_mode.html_manipulator.BeautifulSoup', return_value='soup_mock')
    @patch('openedx.features.offline_mode.html_manipulator.HtmlManipulator._replace_mathjax_link')
    @patch('openedx.features.offline_mode.html_manipulator.HtmlManipulator._replace_static_links')
    @patch('openedx.features.offline_mode.html_manipulator.HtmlManipulator._replace_asset_links')
    def test_process_html(
        self,
        replace_asset_links_mock: MagicMock,
        replace_static_links_mock: MagicMock,
        replace_mathjax_link_mock: MagicMock,
        beautiful_soup_mock: MagicMock,
        replace_iframe_mock: MagicMock,
    ) -> None:
        html_data_mock = 'html_data_mock'
        xblock_mock = Mock()
        temp_dir_mock = 'temp_dir_mock'
        html_manipulator = HtmlManipulator(xblock_mock, html_data_mock, temp_dir_mock)
        expected_result = 'soup_mock'

        result = html_manipulator.process_html()

        replace_asset_links_mock.assert_called_once_with()
        replace_static_links_mock.assert_called_once_with()
        replace_mathjax_link_mock.assert_called_once_with()
        beautiful_soup_mock.assert_called_once_with(html_manipulator.html_data, 'html.parser')
        replace_iframe_mock.assert_called_once_with(beautiful_soup_mock.return_value)
        self.assertEqual(result, expected_result)

    @patch('openedx.features.offline_mode.html_manipulator.save_mathjax_to_xblock_assets')
    def test_replace_mathjax_link(self, save_mathjax_to_xblock_assets: MagicMock) -> None:
        html_data_mock = f'<script src="{MATHJAX_CDN_URL}"></script>'
        xblock_mock = Mock()
        temp_dir_mock = 'temp_dir_mock'
        html_manipulator = HtmlManipulator(xblock_mock, html_data_mock, temp_dir_mock)

        expected_html_data_after_replacing = f'<script src="{MATHJAX_STATIC_PATH}"></script>'

        self.assertEqual(html_manipulator.html_data, html_data_mock)

        html_manipulator._replace_mathjax_link()  # lint-amnesty, pylint: disable=protected-access

        save_mathjax_to_xblock_assets.assert_called_once_with(html_manipulator.temp_dir)
        self.assertEqual(html_manipulator.html_data, expected_html_data_after_replacing)

    @patch('openedx.features.offline_mode.html_manipulator.save_asset_file')
    def test_replace_static_links(self, save_asset_file_mock: MagicMock) -> None:
        html_data_mock = '<div class="teacher-image"><img src="/static/images/professor-sandel.jpg"/></div>'
        xblock_mock = Mock()
        temp_dir_mock = 'temp_dir_mock'
        html_manipulator = HtmlManipulator(xblock_mock, html_data_mock, temp_dir_mock)

        expected_html_data_after_replacing = (
            '<div class="teacher-image"><img src="assets/images/professor-sandel.jpg"/></div>'
        )

        self.assertEqual(html_manipulator.html_data, html_data_mock)

        html_manipulator._replace_static_links()  # lint-amnesty, pylint: disable=protected-access

        save_asset_file_mock.assert_called_once_with(
            html_manipulator.temp_dir,
            html_manipulator.xblock,
            '/static/images/professor-sandel.jpg',
            'images/professor-sandel.jpg',
        )
        self.assertEqual(html_manipulator.html_data, expected_html_data_after_replacing)

    @patch('openedx.features.offline_mode.html_manipulator.save_asset_file')
    def test_replace_asset_links(self, save_asset_file_mock: MagicMock) -> None:
        html_data_mock = '<div class="teacher-image"><img src="/assets/images/professor-sandel.jpg"/></div>'
        xblock_mock = Mock()
        temp_dir_mock = 'temp_dir_mock'
        html_manipulator = HtmlManipulator(xblock_mock, html_data_mock, temp_dir_mock)

        expected_html_data_after_replacing = (
            '<div class="teacher-image"><img src="assets/images/professor-sandel.jpg"/></div>'
        )

        self.assertEqual(html_manipulator.html_data, html_data_mock)

        html_manipulator._replace_asset_links()  # lint-amnesty, pylint: disable=protected-access

        save_asset_file_mock.assert_called_once_with(
            html_manipulator.temp_dir,
            html_manipulator.xblock,
            '/assets/images/professor-sandel.jpg',
            'assets/images/professor-sandel.jpg',
        )
        self.assertEqual(html_manipulator.html_data, expected_html_data_after_replacing)

    def test_replace_iframe(self):
        html_data_mock = """
            <iframe class="align-middle" title="${_('YouTube Video')}"
            src="" frameborder="0" allowfullscreen style="display:none;"></iframe>
        """
        soup = BeautifulSoup(html_data_mock, 'html.parser')
        expected_html_markup = """<p><a href="">${_('YouTube Video')}</a></p>"""

        HtmlManipulator._replace_iframe(soup)  # lint-amnesty, pylint: disable=protected-access

        self.assertEqual(f'{soup.find_all("p")[0]}', expected_html_markup)
