import unittest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from .html_manipulator import HtmlManipulator


class HtmlManipulatorTest(unittest.TestCase):

    def setUp(self):
        self.xblock = Mock()
        self.html_data = '''
        <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mathjax@2.7.5/MathJax.js?config=TeX-AMS_HTML"></script>
            </head>
            <body>
                <iframe src="https://example.com/video" title="Example Video"></iframe>
                <img src="/static/img/sample.png">
            </body>
        </html>
        '''
        self.manipulator = HtmlManipulator(self.xblock, self.html_data)

    @patch('html_manipulator.save_asset_file')
    def test_replace_mathjax_link(self, mock_save_asset_file):
        updated_html = self.manipulator._replace_mathjax_link()
        self.assertNotIn('https://cdn.jsdelivr.net/npm/mathjax@2.7.5/MathJax.js', updated_html)
        self.assertIn('src="/static/mathjax/MathJax.js"', updated_html)

    @patch('html_manipulator.save_asset_file')
    def test_replace_static_links(self, mock_save_asset_file):
        updated_html = self.manipulator._replace_static_links()
        self.assertIn('assets/img/sample.png', updated_html)
        mock_save_asset_file.assert_called_with(self.xblock, '/static/img/sample.png', 'img/sample.png')

    def test_replace_iframe(self):
        soup = BeautifulSoup(self.html_data, 'html.parser')
        self.manipulator._replace_iframe(soup)
        self.assertEqual(len(soup.find_all('iframe')), 0)
        self.assertEqual(len(soup.find_all('a', href='https://example.com/video')), 1)

    def test_add_js_bridge(self):
        soup = BeautifulSoup(self.html_data, 'html.parser')
        self.manipulator._add_js_bridge(soup)
        script_tag = soup.find('script', string=lambda text: 'sendMessageToiOS' in text if text else False)
        self.assertIsNotNone(script_tag)
        self.assertIn('sendMessageToAndroid', script_tag.string)

    @patch('html_manipulator.save_asset_file')
    def test_process_html(self, mock_save_asset_file):
        final_html = self.manipulator.process_html()
        soup = BeautifulSoup(final_html, 'html.parser')

        # Check MathJax link replacement
        mathjax_script = soup.find('script', src='/static/mathjax/MathJax.js')
        self.assertIsNotNone(mathjax_script)

        # Check iframe replacement
        iframes = soup.find_all('iframe')
        self.assertEqual(len(iframes), 0)
        anchors = soup.find_all('a', href='https://example.com/video')
        self.assertEqual(len(anchors), 1)

        # Check static link replacement
        img_tag = soup.find('img', src='assets/img/sample.png')
        self.assertIsNotNone(img_tag)
        mock_save_asset_file.assert_called_with(self.xblock, '/static/img/sample.png', 'img/sample.png')

        # Check JS bridge script
        script_tag = soup.find('script', string=lambda text: 'sendMessageToiOS' in text if text else False)
        self.assertIsNotNone(script_tag)
