import json
import logging
import string
import random

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from util.disable_rate_limit import can_disable_rate_limit

from openedx.core.djangoapps.user_api.accounts.api import check_account_exists

from student.views import create_account_with_params
from student.models import CourseEnrollment, EnrollmentClosedError, \
    CourseFullError, AlreadyEnrolledError, UserProfile

from enrollment.views import EnrollmentCrossDomainSessionAuth, \
    EnrollmentUserThrottle, ApiKeyPermissionMixIn

from instructor.views.api import save_registration_code, \
    students_update_enrollment, require_level

from .serializers import BulkEnrollmentSerializer
from .utils import  send_activation_email, ApiKeyHeaderPermissionInToken

from django.contrib.auth import authenticate, login
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.validators  import validate_slug
from opaque_keys.edx.locations import SlashSeparatedCourseKey

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

log = logging.getLogger(__name__)



class CreateUserAccountWithoutPasswordView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = ApiKeyHeaderPermissionInToken,


    def post(self, request):
        """

        """
        #{Prename, surname, email, username}
        data = request.data
        # set the honor_code and honor_code like checked,
        # so we can use the already defined methods for creating an user
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"

        data['name'] = request.data.get('prename')
        email = request.data.get('email')
        username = request.data.get('username')
        validate_slug(username)
        # Handle duplicate email/username
        conflicts = check_account_exists(username=username , email=email)
        if conflicts:
            errors = {"user_message": "User already exists"}
            return Response(errors, status=409)

        try:
            password = ''.join(random.choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits)
                               for _ in range(32))

            data['password'] = password
            data['send_activation_email'] = False

            user = create_account_with_params(request, data)
            # set the user as inactive
            user.is_active = True
            user.first_name = request.data.get('prename')
            user.last_name = request.data.get('surname')
            user.save()
            user_id = user.id
            send_activation_email(request)
        except ValidationError as err:
            # Should only get non-field errors from this function
            assert NON_FIELD_ERRORS not in err.message_dict
            # Only return first error for each field
            errors = {"user_message": "Wrong parameters on user creation"}
            return Response(errors, status=400)
        except ValueError as err:
            errors = {"user_message": "Wrong email format"}
            return Response(errors, status=400)

        response = Response({'user_id': user_id}, status=200)

        return response

class SetActivateUserStatus(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = ApiKeyHeaderPermissionInToken,


    def post(self, request):
        """

        """
        #{user_id, activate status}
        data = request.data
        # set the honor_code and honor_code like checked,
        # so we can use the already defined methods for creating an user
        try:
            user_id = int(data['user_id'])
            user = User.objects.get(id=user_id)
            is_active = True if 'true' == "{}".format(data['is_active']).lower() else False
            user.is_active = is_active
            user.save()
        except  User.DoesNotExist:
            errors = {"user_message": "Wrong id User does not exist"}
            return Response(errors, status=400)

        response = Response({'user_id': user_id, 'is_active': is_active}, status=200)

        return response


@can_disable_rate_limit
class BulkEnrollView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = ApiKeyHeaderPermissionInToken,

    def post(self, request):

        data = request.data
        for key, value in data.iteritems():
            data[key] = str(value)
        #user_id = int(data['user_id'])
        try:
            user_id = int(data['user_id'])
            user = User.objects.get(id=user_id)
        except  User.DoesNotExist:
            errors = {"user_message": "Wrong id User does not exist"}
            return Response(errors, status=400)
        data['identifiers']=user.email
        course_id = data.get('course_id')
        data['courses'] = course_id
        data['action'] = 'enroll'
        data['auto_enroll'] = 'true'
        data['email_students'] = 'true'

        serializer = BulkEnrollmentSerializer(data=request.data)
        if serializer.is_valid():


            request.POST = request.data
            response_dict = {
                'auto_enroll': 'true',
                'email_students': serializer.data.get('email_students'),
                'action': 'enroll',
                'courses': {}
            }

            staff = User.objects.filter(is_staff=True).first()
            if staff is not None:
                staff.backend = "api backend"
                login(request, staff)

            for course in serializer.data.get('courses'):
                response = students_update_enrollment(
                    request, course_id=course
                )

                response_dict['courses'][course] = json.loads(response.content)


            course_id = SlashSeparatedCourseKey.from_deprecated_string(serializer.data.get('courses')[0])
            enrollment_obj = CourseEnrollment.get_enrollment(user, course_id)
            enrollment_obj.is_active = True if 'true' == "{}".format(data['is_active']).lower() else False
            enrollment_obj.mode = data['mode']
            enrollment_obj.save()
            return Response(data={'enrollment_id': enrollment_obj.id }, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


@can_disable_rate_limit
class SetEnrollmentStatus(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = ApiKeyHeaderPermissionInToken,

    def post(self, request):

        data = request.data
        # set the honor_code and honor_code like checked,
        # so we can use the already defined methods for creating an user
        try:
            enroll_id = int(data['enroll_id'])
            enrollment_obj = CourseEnrollment.objects.get(id=enroll_id)
            enrollment_obj.is_active = True if 'true' == "{}".format(data['is_active']).lower() else False
            enrollment_obj.save()
        except  User.DoesNotExist:
            errors = {"user_message": "Wrong id User does not exist"}
            return Response(errors, status=400)


        return Response(data={
            'enrollment_id': enrollment_obj.id, 'status': enrollment_obj.is_active
        }, status=status.HTTP_200_OK)


