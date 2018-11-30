"""
Command to load course overviews.
"""

import json
import logging

from dateutil import parser
from django.core.management.base import BaseCommand, CommandError
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore

from openedx.core.djangoapps.models.course_details import CourseDetails

log = logging.getLogger(__name__)


class MGMTUser(object):
    """
    Values for user ID defaults
    """
    id = ModuleStoreEnum.UserID.mgmt_command


class Command(BaseCommand):
    """
    Example usage:
        $ ./manage.py cms update_course_settings_from_json -j '{.....}' --all --settings=devstack
        $ ./manage.py cms update_course_settings_from_json -j '{.....}' 'edX/DemoX/Demo_Course' --settings=devstack
    """
    args = '<course_id course_id ...>'
    help = 'Updates course settings from json for one or more courses.'

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '-j',
            '--json',
            dest='json_str',
            required=True,
            help='Json string',
        )
        parser.add_argument(
            '--no-validate',
            action='store_false',
            dest='validate',
            default=True,
            help='Don\'t validate json data',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Updates all courses',
        )

    def handle(self, *args, **options):

        try:
            json_data = json.loads(options.pop('json_str'))
        except ValueError:
            raise CommandError(u'Bad json data')

        courses = args
        validate = options['validate']
        update_all = options['all']

        if not len(courses) and not update_all:
            raise CommandError(u'At least one course or --all must be specified.')

        if validate:
            date_keys = (
                'start_date',
                'end_date',
                'enrollment_start',
                'enrollment_end',
            )
            start_date, end_date = None, None
            enrollment_start, enrollment_end = None, None
            for key, value in json_data.items():
                if key not in date_keys:
                    raise CommandError(u'Only {} keys allowed in json'.format(', '.join(date_keys)))
                else:
                    try:
                        if value is not None:
                            parser.parse(value)
                    except ValueError:
                        raise CommandError(u'Bad {} value for `{}` field'.format(value, key))

                if key == 'start_date':
                    start_date = parser.parse(value)
                elif key == 'end_date':
                    end_date = parser.parse(value)
                elif key == 'enrollment_start':
                    enrollment_start = parser.parse(value)
                elif key == 'enrollment_end':
                    enrollment_end = parser.parse(value)

            if (end_date and enrollment_start) and (end_date <= enrollment_start):
                raise CommandError(u'`end_date` should be > `enrollment_start`')

            if (start_date and end_date) and (start_date >= end_date):
                raise CommandError(u'`end_date` should be > `start_date`')

            if (enrollment_start and enrollment_end) and (enrollment_start >= enrollment_end):
                raise CommandError(u'`enrollment_end` should be > `enrollment_start`')

            if (end_date and enrollment_end) and (end_date < enrollment_end):
                raise CommandError(u'`enrollment_end` should be < `end_date`')

        if update_all:
            course_keys = [course.id for course in modulestore().get_course_summaries()]
        else:
            course_keys = []
            for course_key in courses:
                try:
                    course_keys.append(CourseKey.from_string(course_key))
                except InvalidKeyError:
                    raise CommandError(u'Invalid key specified: {}'.format(course_key))

        log.info(course_keys)
        for course_key in course_keys:
            log.info(u'Updating %s...', course_key)

            course_data = modulestore().get_course(course_key)
            if not course_data:
                raise CommandError(u'Invalid course: {}'.format(course_key))

            course_details = CourseDetails.populate(course_data)
            json_data['intro_video'] = course_details.intro_video
            course_details.update_from_json(course_key, json_data, MGMTUser)

        log.info(u'Updated successfully.')
