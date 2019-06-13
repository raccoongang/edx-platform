"""
API end-point for creating a new user without password.
"""

from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from social_django.models import UserSocialAuth

from enrollment.api import add_enrollment, get_enrollment, update_enrollment
from enrollment.views import ApiKeyPermissionMixIn
from lms.djangoapps.instructor.views.tools import get_student_from_identifier
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from student.models import UserProfile
from third_party_auth.models import OAuth2ProviderConfig


class CreateUserAccountWithoutPasswordView(APIView):
    """
    API endpoint for user provisioning.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    def post(self, request):
        """
        Create user by email, username and uid.
        """
        data = request.data
        email = data.get('email')
        username = data.get('username')
        uid = data.get('uid')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        full_name = "{} {}".format(first_name, last_name).strip() if first_name or last_name else username

        if check_account_exists(username=username, email=email):
            check_list = check_account_exists(username=username, email=email)
            data = {"error_message": "{} already exists".format(" and ".join(check_list).capitalize())}
            response_status = status.HTTP_409_CONFLICT
        elif UserSocialAuth.objects.filter(uid=uid).exists():
            data = {"error_message": "Parameter 'uid' isn't unique."}
            response_status = status.HTTP_400_BAD_REQUEST
        else:
            try:
                user = User.objects.create_user(
                    username=username, email=email, password=uuid4().hex, first_name=first_name, last_name=last_name
                )
                user_profile = UserProfile.objects.create(user=user)
                user_profile.name = full_name
                user_profile.allow_certificate = True
                user_profile.save()
                idp_name = OAuth2ProviderConfig.objects.first().backend_name
                UserSocialAuth.objects.create(user=user, provider=idp_name, uid=uid)
                data = {'user_id': user.id, 'username': username}
                response_status = status.HTTP_200_OK
            except (ValueError, ValidationError) as e:
                return Response(
                    data={"error_message": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(data=data, status=response_status)


class UserEnrollView(APIView, ApiKeyPermissionMixIn):
    """
    API endpoint for enrolling/unenrolling user on the course.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    def post(self, request):
        """
        Enroll/unenroll user on the course using user_email, course mode and course_id.
        """
        data = request.data
        user_email = data.get('user_email')
        mode = data.get('mode')
        course_id = data.get('course')
        is_active = "{}".format(data.get('is_active')) if data.get('is_active') else 'True'
        try:
            user = get_student_from_identifier(user_email)
            if is_active not in ['True', 'False']:
                raise ValueError("'is_active' parametr must be 'True' or 'False'.")
            else:
                is_active = eval(is_active)
            if not get_enrollment(user, course_id):
                add_enrollment(user, course_id, mode, is_active)
                data = {
                    'user': user_email, 'course': course_id, 'status': "Success enroll (is_active={})".format(is_active)
                }
            else:
                update_enrollment(user, course_id, mode, is_active)
                data = {
                    'user': user_email, 'course': course_id, 'status': "Success enroll (is_active={})".format(is_active)
                }
            request_status = status.HTTP_200_OK
            return Response(data=data, status=request_status)
        except User.DoesNotExist:
            return Response(
                data={"error_message": 'User with email - {user_email} does not exist'.format(user_email=user_email)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            return Response(
                data={"error_message": 'Problem with enrolling user. Error: {ex}'.format(ex=ex.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
