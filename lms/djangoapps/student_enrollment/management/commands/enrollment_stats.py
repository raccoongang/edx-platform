"""
A command that will notify the marketing team of the enrollment stats for the
5DCC of the 5DCC on a weekly basis.

This command will run every Monday morning at 09:00. It will send an email to
Ciara containing the following information -

    `number_of_students_enrolled`
    `number_of_students_logged_in`
    `total_percentage`
"""
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import CourseEnrollment
from ci_program.api import get_courses_locators_for_program


class Command(BaseCommand):

    help = 'Generate the enrollment stats for the 5DCC and email them to marketing'

    def get_email_body(self):
        """
        Generate the main body text for the email
        """
        self.total_enrolled_text = "Total number of enrollments: {}\n".format(
            self.number_of_students_enrolled
        )

        self.total_logged_in_text = "Total number of log ins: {}\n".format(
            self.number_of_students_logged_in
        )

        self.total_percentage_text = "Total percentage: {}\n".format(
            self.total_percentage
        )
        
        self.email_body = self.total_enrolled_text + self.total_logged_in_text + self.total_percentage_text

    def prep_email_context(self):
        """
        A convenience method that will just initiate the variables required
        for the email (to, from, subject, body)
        """
        self.to_address = "aaron@codeinstitute.net"
        self.from_address = "learning@codeinstitute.net"
        self.subject = "Login numbers for 5DCC"
        self.get_email_body()
    
    def get_statistics(self, module_locator):
        """
        Get the statistics on the number of students that were enrolled,
        the number of students that were logged in and the total percentage
        of students
        """
        # Get all of the enrollment records for this run of the 5DCC
        self.module_enrollment_records = CourseEnrollment.objects.filter(
            course_id__icontains=module_locator)
        
        # Set the default values
        self.number_of_students_enrolled = len(self.module_enrollment_records)
        self.number_of_students_logged_in = 0

        for enrollment in self.module_enrollment_records:
            try:
                if User.objects.get(email=enrollment.user).last_login is not None:
                    self.number_of_students_logged_in += 1
            except User.DoesNotExist:
                continue
        
        self.total_percentage = 100 * float(
            self.number_of_students_logged_in) / float(self.number_of_students_enrolled)

    def handle(self, *args, **options):
        # 5DCC only has one module associated with it so we only care
        # about a single item for the `get_courses_locators_for_program`
        module_locator = get_courses_locators_for_program("5DCC")

        self.get_statistics(module_locator[0])

        self.prep_email_context()        
        
        send_mail(
            self.subject,
            self.email_body,
            self.from_address,
            [self.to_address],
            fail_silently=False,
        )

