from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ci_program.models import Program
from student_enrollment.utils import register_student, get_or_register_student
from student_enrollment.serializers import EnrollmentSerializer
from django.contrib.auth.models import User


class Student:

    def __init__(self, email, full_name, course_code):
        self.email = email
        self.full_name = full_name
        self.course_code = course_code


class StudentEnrollment(APIView):

    def post(self, request):
        data = request.data
        serializer = EnrollmentSerializer(data=data)

        if serializer.is_valid():
            user = Student(serializer.data['email'], serializer.data['full_name'], serializer.data['course_code'])
            program = Program.objects.get(
                zoho_program_code=user.course_code)
            
            user, password, enrollment_type = get_or_register_student(
                user)

            program_enrollment_status = program.enroll_student_in_program(
                user)
            
            email_sent_status = program.send_email(
                user, 0, password)
            
            return Response(
                {
                    "enrollment_sucess": bool(program_enrollment_status),
                    "email_sucess": bool(email_sent_status),
                    "status": status.HTTP_201_CREATED
                }
            )
        else:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST
                }
            )
            

    
    

    