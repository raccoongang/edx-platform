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
from opaque_keys import InvalidKeyError
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from student.forms import PasswordResetFormNoActive
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser

log = logging.getLogger(__name__)

def string_to_boolean(string):
    return bool(string) and str(string).lower() == 'true'


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
        email = request.data.get('email')
        username = request.data.get('username')
        prename = request.data.get('prename', '')
        surname = request.data.get('surname', '')
        if not username:
            return Response(data={"user_message": "'username' is required parameter."}, status=400)

        if not email:
            return Response(data={"user_message": "'email' is required parameter."}, status=400)

        try:
            validate_slug(username)
        except ValidationError:
            return Response(
                data={
                    "user_message": "Enter a valid 'username' consisting of letters, numbers, underscores or hyphens."
                },
                status=400
            )

        data['name'] =  "{} {}".format(prename, surname).strip() if prename or surname else username

        if check_account_exists(username=username, email=email):
            return Response(data={"user_message": "User already exists"}, status=409)

        try:
            data['password'] = uuid4().hex
            user = create_account_with_params(request, data)
            user.is_active = True
            user.first_name = prename
            user.last_name = surname
            user.save()
            self.send_activation_email(request)
        except ValidationError:
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
        user_id = data.get('user_id')
        if not user_id:
            return Response(data={"user_message": "'user_id' is required parameter."}, status=400)

        try:
            user = User.objects.get(id=user_id)
            user.is_active = string_to_boolean(data.get('is_active'))
            user.save()
        except  User.DoesNotExist:
            return Response(data={"user_message": "Wrong 'user_id'. User does not exist"}, status=400)

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
        user_id = data.get('user_id')
        course_id = data.get('course_id')
        if not user_id:
            return Response(data={"user_message": "'user_id' is required parameter."}, status=400)

        if not course_id:
            return Response(data={"user_message": "'course_id' is required parameter."}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except  User.DoesNotExist:
            return Response(data={"user_message": "Wrong 'user_id'. User does not exist"}, status=400)

        try:
            course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)
            enrollment_obj, __ = CourseEnrollment.objects.update_or_create(
                user=user,
                course_id=course_id,
                defaults={
                    'mode': data.get('mode', 'honor'),
                    'is_active': string_to_boolean(data.get('is_active'))
                }
            )
        except InvalidKeyError:
            return Response(data={"user_message": "Wrong 'course_id'. Course does not exist"}, status=400)

        return Response(data={'enrollment_id': enrollment_obj.id}, status=status.HTTP_200_OK)
