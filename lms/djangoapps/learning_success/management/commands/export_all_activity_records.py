from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from opaque_keys.edx.locator import CourseLocator
from xmodule.modulestore.django import modulestore

from collections import Counter
from datetime import datetime, timedelta
import json

import requests


MODULE_LOCATORS = {
    'HTML Fundamentals':
        CourseLocator(u'CodeInstitute', u'HF101', u'2017_T1'),
    'CSS Fundamentals':
        CourseLocator(u'CodeInstitute', u'CF101', u'2017_T1'),
    'JavaScript Fundamentals':
        CourseLocator(u'CodeInstitute', u'JSF101', u'2017_T1'),
    'Python Fundamentals':
        CourseLocator(u'CodeInstitute', u'PF101', u'2017_T1'),
    'User Centric Frontend Development':
        CourseLocator(u'codeinstitute', u'FE', u'2017_T3'),
    'Interactive Frontend Development':
        CourseLocator(u'CodeInstitute', u'IFD101', u'2017_T3'),
    'Practical Python':
        CourseLocator(u'CodeInstitute', u'BD101', u'2017_T1'),
    'Data Centric Development':
        CourseLocator(u'CodeInstitute', u'DCP101', u'2017_T3'),
    'Full Stack Frameworks With Django':
        CourseLocator(u'CodeInstitute', u'F101', u'2017_T1'),
    '5 Day Coding Challenge':
        CourseLocator(u'CodeInstitute', u'5DCC', u'T1_2018'),
}


def harvest_course_tree(tree, output_dict, prefix=()):
    """Recursively harvest the breadcrumbs for each component in a tree

    Populates output_dict
    """
    block_name = tree.display_name
    block_breadcrumbs = prefix + (tree.display_name,)
    block_id = tree.location.block_id

    children = tree.get_children()
    for subtree in children:
        harvest_course_tree(subtree, output_dict, prefix=block_breadcrumbs)
    if not children:  # a leaf block AKA component
        output_dict[block_id] = block_breadcrumbs


def harvest_program(locators):
    """Harvest the breadcrumbs from all components in the list of locators

    Returns a dictionary mapping block IDs to the matching breadcrumbs
    """
    all_blocks = {}
    for course_locator in locators:
        course = modulestore().get_course(course_locator)
        harvest_course_tree(course, all_blocks)
    return all_blocks


def format_date(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def format_module_units_field(module_name):
    return module_name.lower().replace(' ', '_') + '_units'


def thirty_day_units(student, completion_timestamps):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    return sum(date > thirty_days_ago for date in completion_timestamps)


def days_into_data(student, completion_timestamps):
    days_into_generator = ((date - student.date_joined).days
                           for date in completion_timestamps)
    return ','.join(map(str, sorted(days_into_generator)))


def completed_units_per_module(breadcrumb_list):
    return Counter(format_module_units_field(breadcrumbs[0])
                   for breadcrumbs in breadcrumb_list)


def all_student_data(all_components):
    """Yield a progress metadata dictionary for each of the students

    Input is a pregenerated dictionary mapping block IDs in LMS to breadcrumbs
    """
    for student in User.objects.all():
        # Provide default values in cases where student hasn't started
        latest_unit_complete, latest_unit_breadcrumbs = (None, (u'',)*4)
        # Dictionary of breadcrumbs to timestamps of completion
        completed_units = {}
        for activity in student.studentmodule_set.order_by('modified'):
            block_id = activity.module_state_key.block_id
            breadcrumbs = all_components.get(block_id)
            if breadcrumbs:
                # we only care about the unit level (depth 4)
                unit_breadcrumbs = breadcrumbs[:4]
                # for each unit learned, store latest timestamp
                completed_units[unit_breadcrumbs] = activity.modified
                # remember details of the latest unit overall
                latest_unit_complete = activity.modified
                latest_unit_breadcrumbs = unit_breadcrumbs

        student_dict = {
            'email': student.email,
            'date_joined': format_date(student.date_joined),
            'last_login': format_date(student.last_login),
            'latest_unit_completion': format_date(latest_unit_complete),
            'latest_module': latest_unit_breadcrumbs[0].encode('utf-8'),
            'latest_section': latest_unit_breadcrumbs[1].encode('utf-8'),
            'latest_lesson': latest_unit_breadcrumbs[2].encode('utf-8'),
            'latest_unit': latest_unit_breadcrumbs[3].encode('utf-8'),
            'units_in_30d': thirty_day_units(student, completed_units.values()),
            'days_into_data': days_into_data(student, completed_units.values()),
        }

        student_dict.update(completed_units_per_module(completed_units.keys()))
        yield student_dict


class Command(BaseCommand):
    help = 'Extract student data from the open-edX server for use in Strackr'

    def handle(self, *args, **options):
        """POST the collected data to the api endpoint from the settings
        """
        all_components = harvest_program(MODULE_LOCATORS.values())
        student_data = list(all_student_data(all_components))

        api_endpoint = settings.STRACKR_LMS_API_ENDPOINT
        resp = requests.post(api_endpoint, data=json.dumps(student_data))
        if resp.status_code != 200:
            raise CommandError(resp.text)
