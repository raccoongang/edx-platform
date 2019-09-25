"""
Setup for configurate notexblock XBlock package.
"""

from __future__ import absolute_import

import os
from setuptools import setup


def package_data(pkg, roots):
    """
    Find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="ucdc_edx_api",
    version="0.1.0",
    description="Edx plugin to provide public API for UCDC portal.",
    long_description=README,
    packages=["ucdc_edx_api"],
    install_requires=[],
    requires=[],
    entry_points={
        "lms.djangoapp": ["ucdc_edx_api = ucdc_edx_api.apps:ApiConfig"],
    },
)
