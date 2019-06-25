import os
from .common import *


STATIC_ROOT = os.environ.get('STATIC_ROOT')

DATABASES = {
    'default': {'ENGINE': None}
}

LOCALE_PATHS = os.environ.get('LOCALE_PATHS').split(';')

INSTALLED_APPS.remove('edxmako.apps.EdxMakoConfig')
