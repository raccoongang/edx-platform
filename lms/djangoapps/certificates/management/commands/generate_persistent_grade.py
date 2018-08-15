"""
Management command which update/generate persistent grades
"""
import logging

from django.core.management.base import BaseCommand
from django.http import Http404
from lms.djangoapps.grades.new.course_grade import CourseGradeFactory

from course_blocks.api import get_course_blocks
from courseware import courses
from student.models import User, CourseEnrollment

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command which update/generate persistent grades
    """

    help = """
    Update/generate persistent grades
    """

    def handle(self, *args, **options):
        for enrollment in CourseEnrollment.objects.all():
            user = enrollment.user
            try:
                course = courses.get_course_by_id(enrollment.course_id)
                course_structure = get_course_blocks(user, course.location)
            except:
                # Used for catch exceptions related to bad courses
                pass
            # Used for ignoring student that doesn't enrol in given course
            if len(course_structure) > 0:
                CourseGradeFactory().update(user, course, course_structure)
