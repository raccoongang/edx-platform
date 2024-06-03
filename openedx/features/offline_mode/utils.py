import os
import logging

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from zipfile import ZipFile


from .assets_management import base_storage_path, remove_old_files, is_modified
from .html_manipulator import HtmlManipulator

User = get_user_model()
log = logging.getLogger(__name__)


def create_zip_file(base_path, file_name):
    zf = ZipFile(default_storage.path(base_path + file_name), 'w')
    zf.write(default_storage.path(base_path + 'index.html'), 'index.html')

    def add_files_to_zip(zip_file, current_base_path, current_path_in_zip):
        try:
            directories, files = default_storage.listdir(current_base_path)
        except OSError:
            return

        for file_name in files:
            full_path = os.path.join(current_base_path, file_name)
            zip_file.write(full_path, os.path.join(current_path_in_zip, file_name))

        for directory in directories:
            add_files_to_zip(zip_file, os.path.join(current_base_path, directory),
                             os.path.join(current_path_in_zip, directory))

    add_files_to_zip(zf, default_storage.path(base_path + 'assets/'), 'assets')
    zf.close()


def generate_offline_content(xblock, html_data):
    if not is_modified(xblock):
        return

    base_path = base_storage_path(xblock)
    remove_old_files(xblock)
    html_manipulator = HtmlManipulator(xblock, html_data)
    updated_html = html_manipulator.process_html()

    default_storage.save(
        os.path.join(base_path, 'index.html'),
        ContentFile(updated_html),
    )
    create_zip_file(base_path, 'offline_content.zip')
