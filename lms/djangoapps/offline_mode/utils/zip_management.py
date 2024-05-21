import os
import zipfile
from django.core.files.storage import default_storage


def create_zip_file(base_path, file_name):
    zf = zipfile.ZipFile(default_storage.path(base_path + file_name), "w")
    zf.write(default_storage.path(base_path + "index.html"), "index.html")

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

    add_files_to_zip(zf, default_storage.path(base_path + "assets/"), 'assets')
    zf.close()
