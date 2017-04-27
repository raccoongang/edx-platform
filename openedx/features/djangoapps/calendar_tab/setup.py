import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="calendar-tab",
    version="0.1",
    install_requires=["setuptools"],
    requires=[],
    packages=["calendar_tab"],
    description='Edx Calendar tab',
    long_description=README,
    entry_points={
        "openedx.course_tab": [
            "calendar = calendar_tab.plugins:CalendarTab"
        ]
    }
)
