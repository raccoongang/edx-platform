import os
from .common import *


STATIC_ROOT = os.environ.get('STATIC_ROOT')

DATABASES = {
    'default': {'ENGINE': None}
}
