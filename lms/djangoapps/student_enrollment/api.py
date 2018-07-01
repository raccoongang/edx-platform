from datetime import date
from logging import getLogger
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ci_program.models import Program
from student_enrollment.utils import register_student, get_or_register_student
from student_enrollment.serializers import EnrollmentSerializer
from django.contrib.auth.models import User

log = getLogger(__name__)

FAILURE_CODES = (
    (0, "Email already exists"),
    (1, "Program code not found"),
    (2, "Enrollment may only occur on a Monday"),
    (3, "User creation failed"),
    (4, "Failed to enroll student in program"),
    (5, "Failed to send email")
)


class Student:
    """
    A convenience class that we'll deserialize the student object
    so we can store the data in this `Student` object
    """

    def __init__(self, email, course_code, manual_override=False):
        self.email = email
        self.course_code = course_code
        self.manual_override = manual_override


class StudentEnrollment(APIView):
    """
    The main API handler view class for the enrollment API. This API
    will enroll a given student in a program using the email address
    and program code provided.
    """

    def post(self, request):
        
        log.info("Received request from enrollment API")
        data = request.data
        serializer = EnrollmentSerializer(data=data)

        if serializer.is_valid():
            log.info("Deserialized data is valid. Commencing enrollment")
            
            # Bind the deserialised data to an instance of the above
            # `Student` object
            student = Student(
                serializer.data['email'],
                serializer.data['course_code'],
                serializer.data['manual_override']
            )
            
            # The automated enrollment process for the 5DCC should only
            # occur on a Monday. In order to achieve this, need to check to
            # sure that it is the 5DCC enrollment that is being requested.
            # If so, we need to check to see if current day is a Monday. Or
            # if a manual override has been provided (this may be needed in)
            # the event that a student was late for enrollment, or an issue
            # occurred that the process wasn't able to recover from.
            # If not, the API will issue a response with an API specific
            # status code and reason for failure, along with an HTTP status
            # of 500. Otherwise create an entry in the log as proceed as
            # normal
            if student.course_code == "5DCC":
                if date.today().weekday() == 0 or student.manual_override:
                    log.info("Zap request received for %s" % student.email)
                else:
                    log.info(
                        "Attempted to enroll student outside of Monday")
                    return Response(
                            {
                            "enrollment_status": FAILURE_CODES[3][0],
                            "reason": FAILURE_CODES[3][1]
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Try to retrieve the course that request wants to enroll
            # the student in. If one isn't found then return a 404
            # along with the possible program codes to suggest an
            # alternative
            try:
                program = Program.objects.get(
                    program_code=student.course_code)
            except Program.DoesNotExist as e:
                log.info("Program `%s` does not exist" % student.course_code)
                program_codes = [program.program_code for program in program.objects.all()]
                
                return Response(
                    {
                        "enrollment_status": FAILURE_CODES[2][0],
                        "reason": FAILURE_CODES[2][1],
                        "program_codes": program_codes 
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Create the user and get their password so they can be
            # emailed to the student later
            log.info("Creating user for %s" % student.email)
            user, password, _ = get_or_register_student(student)
            
            # If `None` was returned instead of a user instance then
            # respond with a 500 error and the corresponding failure
            # reason
            if user:
                log.info("User created successfully for %s" % student.email)
            else:
                log.info("User creation failed for %s" % student.email)
                return Response(
                    {
                        "enrollment_status": FAILURE_CODES[4][0],
                        "reason": FAILURE_CODES[4][1]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Enroll the new student into the chosen program
            log.info("Enrolling %s into %s" % (student.email, program.name))
            program_enrollment_status = program.enroll_student_in_program(
                student.email)
            
            # If the enrollment was successful then continue as usual,
            # otherwise issue a 500 response
            if program_enrollment_status:
                log.info("%s successfully enrolled in %s" % (
                    student.email, program.name))
            else:
                log.info("Unable to enroll %s in %s" % (
                    student.email, program.name))
                return Response(
                    {
                        "enrollment_status": FAILURE_CODES[5][0],
                        "reason": FAILURE_CODES[5][1]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Send the email to the student
            log.info("Sending login credentials to %s" % student.email)
            email_sent_status = program.send_email(
                user, 0, password)
            
            # Check to see if the email was sent and if theyn't then
            # respond with a 500 error
            if email_sent_status:
                log.info("Email was successfully sent from the LMS")
            else:
                log.info("Email sending failure")
                return Response(
                    {
                        "enrollment_status": FAILURE_CODES[6][0],
                        "reason": FAILURE_CODES[6][1]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Everything went well so return a status of 201 as well
            # as some basic information
            return Response(
                {
                    "enrollment_success": bool(program_enrollment_status),
                    "email_success": bool(email_sent_status)
                },
                status=status.HTTP_201_CREATED
            )
        else:
            log.warn("Data deserialisation unsuccessful - %s" % request.data)
            print(request.data)
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )