# -*- coding: utf-8 -*-

"""
Common tokens go here.
"""
import json

from path import Path as path


PROJECT_ROOT = path(__file__).abspath().dirname().dirname()  # /edx-platform/common
EDEOS_AUTH_FILENAME = "edeos"

with open(PROJECT_ROOT / EDEOS_AUTH_FILENAME + ".env.json") as edeos_env_file:
    EDEOS_AUTH_ENV_TOKENS = json.load(edeos_env_file)
