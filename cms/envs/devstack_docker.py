""" Overrides for Docker-based devstack. """

from .devstack import *  # pylint: disable=wildcard-import, unused-wildcard-import
from .common import _make_mako_template_dirs


ENABLE_COMPREHENSIVE_THEMING = True
COMPREHENSIVE_THEME_DIRS = [
    "/edx/app/edx-themes/"
]
DEFAULT_SITE_THEME = 'edx-theme'
TEMPLATES[1]["DIRS"] = _make_mako_template_dirs
ELASTIC_SEARCH_CONFIG = [
    {
        'use_ssl': False,
        'host': 'elasticsearch7.devstack.edx',
        'port': 9200
    }
]
derive_settings(__name__)
