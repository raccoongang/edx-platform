import os
from django.conf import settings


def get_static_file_path(relative_path):
    base_path = settings.STATIC_ROOT
    return os.path.join(base_path, relative_path)


def read_static_file(path):
    with open(path, 'rb') as file:
        return file.read()
