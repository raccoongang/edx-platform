import logging
from uuid import uuid4
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from student.views import create_account_with_params
from student.models import CourseEnrollment, EnrollmentClosedError, CourseFullError, AlreadyEnrolledError, UserProfile
from enrollment.views import EnrollmentCrossDomainSessionAuth, EnrollmentUserThrottle, ApiKeyPermissionMixIn
from django.core.validators import validate_slug
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from student.forms import PasswordResetFormNoActive
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser

log = logging.getLogger(__name__)

def string_to_boolean(string):
    return str(string).lower() in ['true',]


class CreateUserAccountWithoutPasswordView(APIView):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermission,

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
        try:
            validate_slug(username)
        except ValidationError as err:
            return Response(data={"user_message": " ".join(err.messages)}, status=400)

        if check_account_exists(username=username, email=email):
            return Response(data={"user_message": "User already exists"}, status=409)

        try:
            data['password'] = uuid4().hex
            user = create_account_with_params(request, data)
            user.is_active = True
            user.first_name = request.data.get('prename')
            user.last_name = request.data.get('surname')
            user.save()
            self.send_activation_email(request)
        except ValidationError as err:
            # Should only get non-field errors from this function
            assert NON_FIELD_ERRORS not in err.message_dict
            # Only return first error for each field
            return Response(data={"user_message": "Wrong parameters on user creation"}, status=400)
        except ValueError as err:
            return Response(data={"user_message": "Wrong email format"}, status=400)

        return Response(data={'user_id': user.id}, status=200)

    @staticmethod
    def send_activation_email(request):
        form = PasswordResetFormNoActive(request.data)
        if form.is_valid():
            form.save(use_https=request.is_secure(),
                      from_email=configuration_helpers.get_value(
                          'email_from_address', settings.DEFAULT_FROM_EMAIL),
                      request=request,
                      subject_template_name='etc_api/set_password_subject.txt',
                      email_template_name='etc_api/set_password_email.html'
                      )


class SetActivateUserStatus(APIView):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermission,

    def post(self, request):
        """
        Enable or disable user by user id.
        """
        data = request.data
        try:
            user = User.objects.get(id=data['user_id'])
            user.is_active = string_to_boolean(data['is_active'])
            user.save()
        except  User.DoesNotExist:
            return Response(data={"user_message": "Wrong id User does not exist"}, status=400)

        return Response(data={'user_id': data['user_id'], 'is_active': user.is_active}, status=200)



class EnrollView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermission,

    def post(self, request):
        """
        Enrolling user on the course with the specified mod.

        Create or update enroll user on the course. Can deactivate enroll
        or activate enroll with use 'is_active' param.
        """
        data = request.data
        try:
            user = User.objects.get(id=data['user_id'])
        except  User.DoesNotExist:
            return Response(data={"user_message": "Wrong id User does not exist"}, status=400)
        course_id = SlashSeparatedCourseKey.from_deprecated_string(data['course_id'])
        enrollment_obj, __ = CourseEnrollment.objects.update_or_create(
            user=user,
            course_id=course_id,
            defaults={
                'mode': data['mode'],
                'is_active': string_to_boolean(data['is_active'])
            }
        )
        return Response(data={'enrollment_id': enrollment_obj.id}, status=status.HTTP_200_OK)