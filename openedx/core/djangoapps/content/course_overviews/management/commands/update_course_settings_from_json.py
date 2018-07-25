"""
Command to load course overviews.
"""

import logging

import json

from django.core.management.base import BaseCommand, CommandError
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from openedx.core.djangoapps.models.course_details import CourseDetails
from xmodule.modulestore import ModuleStoreEnum

log = logging.getLogger(__name__)

class MGMTUser(object):
    """
    Values for user ID defaults
    """
    id = ModuleStoreEnum.UserID.mgmt_command

class Command(BaseCommand):
    """
    Example usage:
        $ ./manage.py cms update_course_settings_from_json '{.....}' --all --settings=devstack
        $ ./manage.py cms update_course_settings_from_json '{.....}' 'edX/DemoX/Demo_Course' --settings=devstack
    """
    args = '<course_id course_id ...>'
    help = 'Updates course settings from json for one or more courses.'

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Updates course settings from json for one or more courses.',
        )

    def handle(self, *args, **options):

        if len(args) < 2:
            raise CommandError('At least one course or --all must be specified.')

	arg0, course_list = args[0], args[1:]
        in_json = json.loads(arg0)

        if options['all']:
            course_keys = [course.id for course in modulestore().get_course_summaries()]
        else:
            try:
                course_keys = [CourseKey.from_string(arg) for arg in course_list]
            except InvalidKeyError:
                raise CommandError('Invalid key specified.')

        for course_key in course_keys:
            log.info("Updating %s...", course_key)

            cd = CourseDetails.fetch(course_key)
            in_json["intro_video"] = cd.intro_video
            cd.update_from_json(course_key, in_json, MGMTUser)

        log.info("Updated successfully.")
