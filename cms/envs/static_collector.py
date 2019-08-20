import os
from openedx.core.lib.derived import derive_settings
from .common import *


STATIC_ROOT = os.environ.get('STATIC_ROOT')

DATABASES = {
    'default': {'ENGINE': None}
}

LOCALE_PATHS = os.environ.get('LOCALE_PATHS').split(';')
derive_settings(__name__)
