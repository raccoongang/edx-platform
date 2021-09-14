import re
import zipfile

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.exceptions import ItemNotFoundError


class HtmlBlockMobileApiMixin:
    FILE_NAME = 'content_html.zip'

    def update_info_api(self):
        if not self.is_modified():
            return

        base_path = self._base_storage_path()
        self.remove_old_files(base_path)

        def replace_static_links(match):
            link = match.group()
            filename = link.split('/static/')[-1]
            self.save_asset_file(link, filename)
            return f'assets/{filename}'

        def replace_iframe(data):
            soup = BeautifulSoup(data, 'html.parser')
            for node in soup.find_all('iframe'):
                replacement = soup.new_tag('p')
                tag_a = soup.new_tag('a')
                tag_a['href'] = node.get('src')
                tag_a.string = node.get('title', node.get('src'))
                replacement.append(tag_a)
                node.replace_with(replacement)
            return str(soup)

        pattern = re.compile(r'/static/[\w\+@\-_\.]+')
        data = pattern.sub(replace_static_links, self.data)
        data = replace_iframe(data)

        default_storage.save(f'{base_path}index.html', ContentFile(data))
        self.create_zip_file(base_path)

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
        asset_key = StaticContent.get_asset_key_from_path(self.location.course_key, path)
        try:
            content = AssetManager.find(asset_key)
        except (ItemNotFoundError, NotFoundError):
            pass
        else:
            base_path = self._base_storage_path()
            default_storage.save(f'{base_path}assets/{filename}', ContentFile(content.data))

    def create_zip_file(self, base_path):
        zf = zipfile.ZipFile(default_storage.path(base_path + self.FILE_NAME), "w")
        zf.write(default_storage.path(base_path + "index.html"), "index.html")

        try:
            directories, files = default_storage.listdir(base_path + 'assets/')
        except OSError:
            pass
        else:
            for file_name in files:
                zf.write(default_storage.path(base_path + 'assets/' + file_name), 'assets/' + file_name)

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
            self.update_info_api()

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
