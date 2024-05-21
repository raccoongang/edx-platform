import os
from django.conf import settings


def get_static_file_path(relative_path):
    """
    Constructs the absolute path for a static file based on its relative path.
    """
    base_path = settings.STATIC_ROOT
    return os.path.join(base_path, relative_path)


def read_static_file(path):
    """
    Reads the contents of a static file in binary mode.
    """
    with open(path, 'rb') as file:
        return file.read()
