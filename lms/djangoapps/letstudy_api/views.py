"""
API end-point for creating a new user without password.
"""
import logging
from uuid import uuid4
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from opaque_keys import InvalidKeyError
from social_django.models import UserSocialAuth

from enrollment.api import add_enrollment, get_enrollment
from enrollment.views import ApiKeyPermissionMixIn
from lms.djangoapps.instructor.views.tools import get_student_from_identifier
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from student.models import UserProfile
from third_party_auth.models import OAuth2ProviderConfig

log = logging.getLogger(__name__)


class CreateUserAccountWithoutPasswordView(APIView):
    """
    Create user account.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    _error_dict = {
        "username": "Username is required parameter.",
        "email": "Email is required parameter.",
        "uid": "Uid is required parameter."
    }

    def _check_available_required_params(self, parameter, parameter_name, values_list=None):
        """
        Check required parameter is correct.
        If parameter isn't correct ValueError is raised.
        :param parameter: object
        :param parameter_name: string. Parameter's name
        :param values_list: List of values
        :return: parameter
        """
        if not parameter or (values_list and isinstance(values_list, list) and parameter not in values_list):
            raise ValueError(self._error_dict[parameter_name].format(value=parameter))
        return parameter

    def post(self, request):
        """
        Create user by the email and the username.
        """
        data = dict(request.data.iteritems())
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        try:
            email = self._check_available_required_params(request.data.get('email'), "email")
            username = self._check_available_required_params(request.data.get('username'), "username")
            uid = self._check_available_required_params(request.data.get('uid'), "uid")
            if check_account_exists(username=username, email=email):
                return Response(data={"error_message": "User already exists"}, status=status.HTTP_409_CONFLICT)
            if UserSocialAuth.objects.filter(uid=uid).exists():
                return Response(
                        data={"error_message": "Parameter 'uid' isn't unique."},
                        status=status.HTTP_409_CONFLICT
                )
            data['name'] = "{} {}".format(first_name, last_name).strip() if first_name or last_name else username
            data['first_name'] = first_name
            data['last_name'] = last_name
            data['password'] = uuid4().hex
            for param in ('is_active', 'allow_certificate'):
                data[param] = data.get(param, True)
            user = User.objects.create_user(username=username, email=email, password=data['password'])
            UserProfile.objects.create(user=user)
            idp_name = OAuth2ProviderConfig.objects.first().backend_name
            UserSocialAuth.objects.create(user=user, provider=idp_name, uid=uid)
        except (ValueError, ValidationError) as e:
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(data={'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)


class UserEnrollView(APIView, ApiKeyPermissionMixIn):
    """
    API endpoint for enrolling user on the course.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    def post(self, request):
        """
        Enroll user on the course.

        :param course: Course id. string, in the format {key type}:{org}+{course}+{run}.
                                                        For example, course-v1:edX+DemoX+Demo_2014.
        :param user_email: User email string
        :param request: request for Api endpoint
        :param action: string 'enroll'
        :param mode: string indicating what kind of enrollment this is: audit or verified.
        """
        data = request.data
        user_email = data.get('user_email')
        mode = data.get('mode')
        course_id = data.get('course')
        action = data.get('action')
        if action != 'enroll':
            return Response(
                data={"error_message": "Action must be enroll"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = get_student_from_identifier(user_email)

            if get_enrollment(user, course_id):
                return Response(
                    data={
                        "error_message": "User '{user}' has already enrolled on the course '{course}'".format(
                            user=user, course=course_id
                        )
                    },
                    status=status.HTTP_409_CONFLICT
                )

            if mode:
                add_enrollment(user, course_id, mode)
            else:
                return Response(
                    data={"error_message": "Need user mode - 'audit' or 'verified'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = {
                'user': user_email,
                'course': course_id,
                'status': "user was enrolled successfully",
            }

        except User.DoesNotExist:
            return Response(
                data={"error_message": 'User with email - {user_email} does not exist'.format(user_email=user_email)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidKeyError:
            return Response(
                data={
                    "error_message": 'Wrong course_id: {course_id}. Course does not exist'.format(course_id=course_id)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            log.error(ex)
            return Response(
                data={"error_message": 'Problem with enrolling user. Error: {ex}'.format(ex=ex.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(data=result, status=status.HTTP_200_OK)
