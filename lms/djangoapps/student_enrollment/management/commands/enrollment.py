from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings
from ci_program.models import Program
from student_enrollment.utils import (
    get_or_register_student, post_to_zapier
)
from student_enrollment.zoho import (
    get_students,
    parse_course_of_interest_code
)
from lms.djangoapps.student_enrollment.models import EnrollmentStatusHistory
from lms.djangoapps.student_enrollment.models import ProgramAccessStatus


class Command(BaseCommand):
    help = 'Enroll students in their relevant programs'

    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **options):
        """
        The main handler for the program enrollment management command.
        This will retrieve all of the users from the Zoho CRM API and
        will enroll all of the students that have a status of
        `Enrolling`.
        
        If a student doesn't exist in the system then a new a account
        will be registered. A student can be unenrolled from courses
        if they miss payments (or other circumstances) which means they
        may already be registered in the system.
        """

        zoho_students = get_students(status='(Lead Status: Enroll)')

        for student in zoho_students:

            # Get the user, the user's password, and their enrollment type
            user, password, enrollment_type = get_or_register_student(
                student['email'], student['full_name'])

            # Get the code for the course the student is enrolling in
            program_to_enroll_in = parse_course_of_interest_code(
                student.course_of_interest)

            # DITF is not current present in the Learning Platform so
            # we'll skip over it until then
            if 'DITF' in program_to_enroll_in or not program_to_enroll_in:
                continue
            
            # Get the Program that contains the th Zoho program code
            program = Program.objects.get(program_code=program_to_enroll_in)

            # Enroll the student in the program
            program_enrollment_status = program.enroll_student_in_program(
                user.email)

            # Send the email
            email_sent_status = program.send_email(
                user, program.name, enrollment_type, password)

            # Set the students access level (i.e. determine whether or
            # not a student is allowed to access to the LMS.
            access, created = ProgramAccessStatus.objects.get_or_create(
                user=user, program_access=True)

            if not created:
                access.allowed_access = True
                access.save()
            
            post_to_zapier(settings.ZAPIER_ENROLLMENT_URL, user.email)

            enrollment_status = EnrollmentStatusHistory(student=user, program=program, 
                                                        registered=bool(user),
                                                        enrollment_type=enrollment_type,
                                                        enrolled=bool(program_enrollment_status),
                                                        email_sent=email_sent_status)
            enrollment_status.save()