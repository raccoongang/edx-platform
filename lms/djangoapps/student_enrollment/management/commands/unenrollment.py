from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings
from ci_program.models import Program
from student_enrollment.utils import get_or_register_student
from student_enrollment.zoho import (
    get_students,
    parse_course_of_interest_code,
    update_student_record
)
from lms.djangoapps.student_enrollment.models import (
    EnrollmentStatusHistory,
    ProgramAccessStatus
)


class Command(BaseCommand):
    help = 'Unenroll students from their relevant programs'

    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **options):
        """
        The main handler for the program enrollment management command.
        This will retrieve all of the users from the Zoho CRM API and
        will unenroll all of the students that have a status of
        `Unenroll`.
        """

        # The only possible enrollment type here is unenrollment so
        # we'll set the type as a constact
        ENROLLMENT_TYPE = 1

        zoho_students = get_students(status='(Lead Status:Unenroll*)')

        for student in zoho_students:
            # Get the user
            user = User.objects.get(email=student.email)

            # Get the code for the course the student is enrolling in
            program_to_enroll_in = parse_course_of_interest_code(
                student.course_of_interest)

            # DITF is not current present in the Learning Platform so
            # we'll skip over it until then
            if 'DITF' in program_to_enroll_in or not program_to_enroll_in:
                continue
            
            # Check to make sure that the student is enrolled in that program.
            # If they are not enrolled in that program then we can skip this
            # email and move onto the next user
            try:
                user.program_set.get(program_code=program_to_enroll_in)
            except ObjectDoesNotExist:
                print("{} is not enrolled in this {}".format(
                    user.email, program_to_enroll_in))
                continue
            
            # Get the Program that contains the Zoho program code
            program = Program.objects.get(program_code=program_to_enroll_in)

            # Unenroll the student from the program
            program_enrollment_status = program.unenroll_student_from_program(user)

            # Send the email
            email_sent_status = program.send_email(
                user, program.name, enrollment_type)

            # Set the students access level (i.e. determine whether or not a student
            # is allowed to access to the LMS.
            access, created = ProgramAccessStatus.objects.get_or_create(
                user=user, program_access=True)

            if not created:
                access.allowed_access = False
                access.save()
            
            update_student_record(settings.ZAPIER_UNENROLLMENT_URL, user.email)

            # Create a new entry in the EnrollmentStatusHistory to
            # indicate whether or not each step of the process was
            # successful
            enrollment_status = EnrollmentStatusHistory(student=user, program=program, 
                                                        registered=bool(user),
                                                        enrollment_type=ENROLLMENT_TYPE,
                                                        enrolled=bool(program_enrollment_status),
                                                        email_sent=email_sent_status)
            enrollment_status.save()