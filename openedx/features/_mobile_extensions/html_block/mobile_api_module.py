import re
import os
import zipfile

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError


def get_static_file_path(relative_path):
    base_path = settings.STATIC_ROOT
    return os.path.join(base_path, relative_path)


def read_static_file(path):
    with open(path, 'rb') as file:
        return file.read()


class HtmlBlockMobileApiMixin:
    FILE_NAME = 'content_html.zip'

    def update_info_api(self, html_data=None):
        html_data = self.data if not html_data else html_data
        if not self.is_modified():
            return
        base_path = self._base_storage_path()
        self.remove_old_files(base_path)

        # Replace MathJax URL
        mathjax_pattern = re.compile(r'src="https://cdn.jsdelivr.net/npm/mathjax@2.7.5/MathJax.js[^"]*"')
        data = mathjax_pattern.sub(self._replace_mathjax_link, html_data)

        pattern = re.compile(r'/static/[\w./-]+')
        data = pattern.sub(self._replace_static_links, data)

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')
        # Replace iframes
        self._replace_iframe(soup)
        # Add JS bridge script to the HTML data
        self._add_js_bridge(soup)
        # Convert the modified soup back to a string
        data = str(soup)

        default_storage.save(f'{base_path}index.html', ContentFile(data))
        self.create_zip_file(base_path)

    def _replace_static_links(self, match):
        link = match.group()
        filename = link.split('/static/')[-1]
        self.save_asset_file(link, filename)
        return f'assets/{filename}'

    def _replace_mathjax_link(self, match):
        return 'src="/static/mathjax/MathJax.js"'

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
        // Function to send messages to iOS
        function sendMessageToiOS(message) {
            window?.webkit?.messageHandlers?.iOSBridge?.postMessage(message);
        }

        // Function to send messages to Android
        function sendMessageToAndroid(message) {
            window?.AndroidBridge?.postMessage(message);
        }

        // Function to handle messages from iOS
        function receiveMessageFromiOS(message) {
            console.log("Message received from iOS:", message);
            // Handle the message from iOS
        }

        // Function to handle messages from Android
        function receiveMessageFromAndroid(message) {
            console.log("Message received from Android:", message);
            // Handle the message from Android
        }

        // Check if iOS bridge is available
        if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iOSBridge) {
            // iOS bridge is available
            window.addEventListener("messageFromiOS", function(event) {
                receiveMessageFromiOS(event.data);
            });
        }

        // Check if Android bridge is available
        if (window.AndroidBridge) {
            // Android bridge is available
            window.addEventListener("messageFromAndroid", function(event) {
                receiveMessageFromAndroid(event.data);
            });
        }

        const originalAjax = $.ajax;

        $.ajax = function(options) {
            sendMessageToiOS(JSON.stringify(options))
            sendMessageToAndroid(JSON.stringify(options))
            console.log(options, JSON.stringify(options))

            return originalAjax.call(this, options);
        };
        """

        # Insert the script tag before the closing </body> tag
        if soup.body:
            soup.body.append(script_tag)
        else:
            # If there's no body tag, add it to the end of the document
            soup.append(script_tag)

    def remove_old_files(self, base_path):
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

    def _base_storage_path(self):
        return '{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}/'.format(loc=self.location)

    def save_asset_file(self, path, filename):
        try:
            if '/' in filename:
                static_path = get_static_file_path(filename)
                content = read_static_file(static_path)
            else:
                asset_key = StaticContent.get_asset_key_from_path(self.location.course_key, path)
                content = AssetManager.find(asset_key).data
        except (ItemNotFoundError, NotFoundError):
            pass
        else:
            base_path = self._base_storage_path()
            default_storage.save(f'{base_path}assets/{filename}', ContentFile(content))

    def create_zip_file(self, base_path):
        zf = zipfile.ZipFile(default_storage.path(base_path + self.FILE_NAME), "w")
        zf.write(default_storage.path(base_path + "index.html"), "index.html")

        def add_files_to_zip(zip_file, current_base_path, current_path_in_zip):
            try:
                directories, files = default_storage.listdir(current_base_path)
            except OSError:
                return

            # Add files
            for file_name in files:
                full_path = os.path.join(current_base_path, file_name)
                zip_file.write(full_path, os.path.join(current_path_in_zip, file_name))

            # Recursively add directories
            for directory in directories:
                add_files_to_zip(zip_file, os.path.join(current_base_path, directory),
                                 os.path.join(current_path_in_zip, directory))

        add_files_to_zip(zf, default_storage.path(base_path + "assets/"), 'assets')

        zf.close()

    def is_modified(self):
        file_path = f'{self._base_storage_path()}{self.FILE_NAME}'

        try:
            last_modified = default_storage.get_created_time(file_path)
        except OSError:
            return True

        return self.published_on > last_modified

    def student_view_data(self):
        file_path = f'{self._base_storage_path()}{self.FILE_NAME}'

        try:
            default_storage.get_created_time(file_path)
        except OSError:
            # self.update_info_api()
            pass

        html_data = default_storage.url(file_path)

        if not html_data.startswith('http'):
            html_data = f'{settings.LMS_ROOT_URL}{html_data}'

        last_modified = default_storage.get_created_time(file_path)
        size = default_storage.size(file_path)

        return {
            'last_modified': last_modified,
            'html_data': html_data,
            'size': size,
            'index_page': 'index.html',
            'icon_class': self.icon_class,
        }
