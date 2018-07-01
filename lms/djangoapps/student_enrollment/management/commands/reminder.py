"""
A command that will notify zapier of any students that haven't logged in
to get access to the 5DCC yet.

This will be run every Tuesday morning at 09:30, giving the students a
24-hour period to log in before being notified.

This will simply get the locator for the 5DCC run that is currently
associated with the 5DCC program and will iterate over all of the
students that are enrolled in that run of the 5DCC and their email
address will be sent to Zapier, where HubSpot will take over the handling
of sending the emails to the students.
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from student.models import CourseEnrollment
from student_enrollment.utils import post_to_zapier
from ci_program.api import get_courses_locators_for_program


class Command(BaseCommand):
    help = "Send a reminder to students that have yet to log in"
    
    def handle(self, *args, **options):
        """
        Send a reminder to each student that has yet to log in the
        platform.

        The 5DCC will trigger a zap to notify the student's that they
        yet logged in and that they should do so.

        TODO: Implement this same functionality for FS
        """
        for locator in get_courses_locators_for_program("5DCC"):
            course_enrollments = CourseEnrollment.objects.filter(
                course_id=locator)
            for enrollment in course_enrollments:
                print(enrollment.user)
                if enrollment.user.last_login is None:
                    post_to_zapier(settings.ZAPIER_LOGIN_REMINDER,
                        enrollment.user.email)