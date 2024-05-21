import re
from bs4 import BeautifulSoup

from .assets_management import save_asset_file


class HtmlManipulator:
    def __init__(self, xblock, html_data):
        self.html_data = html_data
        self.xblock = xblock

    def _replace_mathjax_link(self):
        mathjax_pattern = re.compile(r'src="https://cdn.jsdelivr.net/npm/mathjax@2.7.5/MathJax.js[^"]*"')
        return mathjax_pattern.sub('src="/static/mathjax/MathJax.js"', self.html_data)

    def _replace_static_links(self):
        pattern = re.compile(r'/static/[\w./-]+')
        return pattern.sub(self._replace_link, self.html_data)

    def _replace_link(self, match):
        link = match.group()
        filename = link.split('/static/')[-1]
        save_asset_file(self.xblock, link, filename)
        return f'assets/{filename}'

    def _replace_iframe(self, soup):
        for node in soup.find_all('iframe'):
            replacement = soup.new_tag('p')
            tag_a = soup.new_tag('a')
            tag_a['href'] = node.get('src')
            tag_a.string = node.get('title', node.get('src'))
            replacement.append(tag_a)
            node.replace_with(replacement)

    def _add_js_bridge(self, soup):
        script_tag = soup.new_tag('script')
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
        self._replace_mathjax_link()
        self._replace_static_links()
        soup = BeautifulSoup(self.html_data, 'html.parser')
        self._replace_iframe(soup)
        self._add_js_bridge(soup)
        return str(soup)
