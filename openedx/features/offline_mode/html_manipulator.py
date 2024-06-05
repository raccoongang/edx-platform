import os
import re

from bs4 import BeautifulSoup

from django.conf import settings

from .assets_management import save_asset_file, save_mathjax_to_local_static
from .constants import MATHJAX_CDN_URL, MATHJAX_STATIC_PATH

RELATIVE_PATH_DIFF = '../../../../'


class HtmlManipulator:
    """
    Class to manipulate the HTML content of an XBlock.


    """

    def __init__(self, xblock, html_data):
        self.html_data = html_data
        self.xblock = xblock

    def _replace_mathjax_link(self):
        """
        Replace MathJax CDN link with local path to MathJax.js file.
        """
        mathjax_pattern = re.compile(fr'src="{MATHJAX_CDN_URL}[^"]*"')
        self.html_data = mathjax_pattern.sub(
            f'src="{RELATIVE_PATH_DIFF}{MATHJAX_STATIC_PATH}"',
            self.html_data
        )

    def _replace_static_links(self):
        """
        Replace static links with local links.
        """
        static_links_pattern = os.path.join(settings.STATIC_URL, '[\w./-]+')
        pattern = re.compile(fr'{static_links_pattern}')
        self.html_data = pattern.sub(self._replace_link, self.html_data)

    def _replace_link(self, match):
        """
        Returns the local path of the asset file.
        """
        link = match.group()
        filename = link.split(settings.STATIC_URL)[-1]
        save_asset_file(self.xblock, link, filename)
        return f'assets/{filename}'

    @staticmethod
    def _replace_iframe(soup):
        """
        Replace iframe tags with anchor tags.
        """
        for node in soup.find_all('iframe'):
            replacement = soup.new_tag('p')
            tag_a = soup.new_tag('a')
            tag_a['href'] = node.get('src')
            tag_a.string = node.get('title', node.get('src'))
            replacement.append(tag_a)
            node.replace_with(replacement)

    @staticmethod
    def _add_js_bridge(soup):
        """
        Add JS bridge script to the HTML content.
        :param soup:
        :return:
        """
        script_tag = soup.new_tag('script')
        # FIXME: this script should be loaded from a file
        script_tag.string = """
        // JS bridge script
        function sendMessageToiOS(message) {
            window?.webkit?.messageHandlers?.iOSBridge?.postMessage(message);
        }
        function sendMessageToAndroid(message) {
            window?.AndroidBridge?.postMessage(message);
        }
        function receiveMessageFromiOS(message) {
            console.log("Message received from iOS:", message);
        }
        function receiveMessageFromAndroid(message) {
            console.log("Message received from Android:", message);
        }
        if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iOSBridge) {
            window.addEventListener("messageFromiOS", function(event) {
                receiveMessageFromiOS(event.data);
            });
        }
        if (window.AndroidBridge) {
            window.addEventListener("messageFromAndroid", function(event) {
                receiveMessageFromAndroid(event.data);
            });
        }
        const originalAjax = $.ajax;
        $.ajax = function(options) {
            sendMessageToiOS(options);
            sendMessageToiOS(JSON.stringify(options));
            sendMessageToAndroid(options);
            sendMessageToAndroid(JSON.stringify(options));
            console.log(options, JSON.stringify(options));
            return originalAjax.call(this, options);
        };
        """
        if soup.body:
            soup.body.append(script_tag)
        else:
            soup.append(script_tag)
        return soup

    def process_html(self):
        """
        Prepares HTML content for local use.

        Changes links to static files to paths to pre-generated static files for offline use.
        """
        save_mathjax_to_local_static()
        self._replace_static_links()
        self._replace_mathjax_link()

        soup = BeautifulSoup(self.html_data, 'html.parser')
        self._replace_iframe(soup)
        self._add_js_bridge(soup)
        return str(soup)
