"""
Management command which update/generate persistent grades.

Usage:
    source ~/edxapp_env ;
    ./manage.py lms generate_persistent_grade --settings=aws
"""
import logging

from django.core.management.base import BaseCommand
from django.http import Http404
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

from course_blocks.api import get_course_blocks
from courseware import courses
from student.models import User, CourseEnrollment

log = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Management command which update/generate persistent grades.
    """

    help = "Update/generate persistent grades"

    def handle(self, *args, **options):
        course_structure = None
        for enrollment in CourseEnrollment.objects.all().iterator():
            user = enrollment.user
            try:
                course = courses.get_course_by_id(enrollment.course_id)
                course_structure = get_course_blocks(user, course.location)
            except Exception as e:
                log.warning(
                    'Persistent grade not generated for the user {} on the course {} because of {}'
                    .format(user.username, enrollment.course_id, e)
                )
            if course_structure:
                try:
                    CourseGradeFactory().update(user, course, course_structure, force_update_subsections=True)
                except Exception as e:
                    log.warning(
                        'Error was occured while updating the course grades: {}'.format(e)
                    )
