from ci_program.api import get_program_by_program_code
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from opaque_keys.edx.locator import CourseLocator
from xmodule.modulestore.django import modulestore

from collections import Counter
from datetime import datetime, timedelta
import json

import requests


PROGRAM_CODE = 'FS'  # Our Full-Stack program


def harvest_course_tree(tree, output_dict, prefix=()):
    """Recursively harvest the breadcrumbs for each component in a tree

    Populates output_dict
    """
    block_name = tree.display_name
    block_breadcrumbs = prefix + (tree.display_name,)
    block_id = tree.location.block_id

    output_dict[block_id] = block_breadcrumbs

    children = tree.get_children()
    for subtree in children:
        harvest_course_tree(subtree, output_dict, prefix=block_breadcrumbs)


def harvest_program(program):
    """Harvest the breadcrumbs from all components in the program

    Returns a dictionary mapping block IDs to the matching breadcrumbs
    """
    all_blocks = {}
    for course_locator in program.get_course_locators():
        course = modulestore().get_course(course_locator)
        harvest_course_tree(course, all_blocks)
    return all_blocks


def format_date(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def thirty_day_units(completion_timestamps):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    return sum(date > thirty_days_ago for date in completion_timestamps)


def days_into_data(first_active, completion_timestamps):
    days_into_generator = (
        (date - first_active).days for date in completion_timestamps)
    return ','.join(map(str, sorted(days_into_generator)))


def format_module_field(module_name, suffix):
    return module_name.lower().replace(' ', '_') + suffix


def completed_lessons_per_module(breadcrumb_dict):
    return Counter(format_module_field(breadcrumbs[0], '_lessons')
                   for breadcrumbs in breadcrumb_dict.keys())


def completed_units_per_module(breadcrumb_dict):
    return Counter(format_module_field(breadcrumbs[0], '_units')
                   for breadcrumbs in breadcrumb_dict.keys())


def all_student_data(program):
    """Yield a progress metadata dictionary for each of the students

    Input is a pregenerated dictionary mapping block IDs in LMS to breadcrumbs
    """
    all_components = harvest_program(program)

    for student in program.enrolled_students.all():
        # A short name for the activities queryset
        student_activities = student.studentmodule_set

        # remember details of the first activity
        first_activity = student_activities.order_by('created').first()
        first_active = (
            first_activity.created if first_activity else student.date_joined)

        # We care about the lesson level (depth 3) and unit level (depth 4).
        # Dictionaries of breadcrumbs to timestamps of completion
        completed_lessons = {}
        completed_units = {}
        # Provide default values in cases where student hasn't started
        latest_unit_started = None
        latest_unit_breadcrumbs = (u'',) * 4
        for activity in student_activities.order_by('modified'):
            block_id = activity.module_state_key.block_id
            breadcrumbs = all_components.get(block_id)
            if breadcrumbs and len(breadcrumbs) == 3:  # lesson
                # for each lesson learned, store latest timestamp
                completed_lessons[breadcrumbs] = activity.modified

            if breadcrumbs and len(breadcrumbs) >= 4:  # unit or inner block
                unit_breadcrumbs = breadcrumbs[:4]
                # for each unit learned, store latest timestamp
                completed_units[unit_breadcrumbs] = activity.modified

                # remember details of the latest unit overall
                # we use 'created' (not 'modified') to ignore backward leaps
                # to old units; sadly, there's no way to ignore forward leaps
                latest_unit_started = activity.created
                latest_unit_breadcrumbs = unit_breadcrumbs

        student_dict = {
            'email': student.email,
            'date_joined': format_date(first_active),
            'last_login': format_date(student.last_login),
            'latest_unit_completion': format_date(latest_unit_started),
            'latest_module': latest_unit_breadcrumbs[0].encode('utf-8'),
            'latest_section': latest_unit_breadcrumbs[1].encode('utf-8'),
            'latest_lesson': latest_unit_breadcrumbs[2].encode('utf-8'),
            'latest_unit': latest_unit_breadcrumbs[3].encode('utf-8'),
            'units_in_30d': thirty_day_units(completed_units.values()),
            'days_into_data': days_into_data(first_active, completed_units.values()),
        }

        student_dict.update(completed_lessons_per_module(completed_lessons))
        student_dict.update(completed_units_per_module(completed_units))

        yield student_dict


class Command(BaseCommand):
    help = 'Extract student data from the open-edX server for use in Strackr'

    def handle(self, *args, **options):
        """POST the collected data to the api endpoint from the settings
        """
        program = get_program_by_program_code(PROGRAM_CODE)
        student_data = list(all_student_data(program))

        api_endpoint = settings.STRACKR_LMS_API_ENDPOINT
        resp = requests.post(api_endpoint, data=json.dumps(student_data))
        if resp.status_code != 200:
            raise CommandError(resp.text)
