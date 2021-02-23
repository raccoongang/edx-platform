"""
Left over environment file from before the transition of devstack from
vagrant to docker was complete.

This file should no longer be used, and is only around in case something
still refers to it.
"""

from .devstack import *  # pylint: disable=wildcard-import, unused-wildcard-import
from .common import _make_mako_template_dirs


ENABLE_COMPREHENSIVE_THEMING = True
COMPREHENSIVE_THEME_DIRS = [
    "/edx/app/edx-themes/"
]
DEFAULT_SITE_THEME = 'edx-theme'
TEMPLATES[1]["DIRS"] = _make_mako_template_dirs
derive_settings(__name__)
