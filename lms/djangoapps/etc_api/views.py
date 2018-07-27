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
from student.models import (
    CourseEnrollment,
    EnrollmentClosedError,
    CourseFullError,
    AlreadyEnrolledError,
    UserProfile
)
from enrollment.views import (
    EnrollmentCrossDomainSessionAuth,
    EnrollmentUserThrottle,
    ApiKeyPermissionMixIn
)
from instructor.views.api import(
    save_registration_code,
    students_update_enrollment,
    require_level
)
from .utils import  send_activation_email, ApiKeyHeaderPermissionInToken
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
        Create user account without password

        Creates a user using mail, login and also name and surname.
        Sets a random password and sends a user a message to change it.
        """
        data = request.data
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"
        data['name'] = request.data.get('prename')
        email = request.data.get('email')
        username = request.data.get('username')
        validate_slug(username)
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
        Enable or disable user by user id.
        """

        data = request.data
        try:
            user_id = int(data['user_id'])
            user = User.objects.get(id=data['user_id'])
            is_active = True if 'true' == "{}".format(data['is_active']).lower() else False
            user.is_active = is_active
            user.save()
        except  User.DoesNotExist:
            errors = {"user_message": "Wrong id User does not exist"}
            return Response(errors, status=400)

        response = Response({'user_id': user_id, 'is_active': is_active}, status=200)

        return response


@can_disable_rate_limit
class EnrollView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = ApiKeyHeaderPermissionInToken,

    def post(self, request):
        """
        Enrolling user on the course with the specified mod.

        Create or update enroll user on the course. Can deactivate enroll
        or activate enroll with use 'is_active' param.
        """
        data = request.data
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
        students_update_enrollment(
            request, course_id=course_id
        )
        course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        enrollment_obj = CourseEnrollment.get_enrollment(user, course_id)
        enrollment_obj.is_active = True if 'true' == "{}".format(data['is_active']).lower() else False
        enrollment_obj.mode = data['mode']
        enrollment_obj.save()
        return Response(data={'enrollment_id': enrollment_obj.id }, status=status.HTTP_200_OK)
