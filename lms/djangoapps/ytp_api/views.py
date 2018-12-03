"""
APIView endpoints for user creating
"""
import logging
from uuid import uuid4

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth

from lms.djangoapps.ytp_api import serializers as ytp_serializer
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from student.views import create_account_with_params
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
        "gender": "Gender parameter must contain 'm'(Male), 'f'(Female) or 'o'(Other. Default if parameter is missing)",
        "uid": "Uid is required parameter."
    }

    def post(self, request):
        """
        Create a user by the email and the username.
        """
        data = request.data
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        try:
            email = self._check_available_required_params(request.data.get('email'), "email")
            username = self._check_available_required_params(request.data.get('username'), "username")
            uid = self._check_available_required_params(request.data.get('uid'), "uid")
            data['gender'] = self._check_available_required_params(
                request.data.get('gender', 'o'), "gender", ['m', 'f', 'o']
            )
            if check_account_exists(username=username, email=email):
                return Response(data={"error_message": "User already exists"}, status=status.HTTP_409_CONFLICT)
            if UserSocialAuth.objects.filter(uid=uid).exists():
                return Response(
                        data={"error_message": "Parameter 'uid' isn't unique."},
                        status=status.HTTP_409_CONFLICT
                )
            data['name'] = "{} {}".format(first_name, last_name).strip() if first_name or last_name else username
            ytp_serializer.UserSerializer().run_validation(data)
            ytp_serializer.ProfileSerializer().run_validation(data)
            data['password'] = uuid4().hex
            user = create_account_with_params(request, data)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.save()
            idp_name = OAuth2ProviderConfig.objects.first().backend_name
            UserSocialAuth.objects.create(user=user, provider=idp_name, uid=uid)
            user = ytp_serializer.UserSerializer().update(user, data)
            ytp_serializer.ProfileSerializer().update(user.profile, data)
        except ValueError as e:
            log.error(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(data={"error_message": e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update user information by uid.
        """
        data = request.data
        try:
            uid = self._check_available_required_params(request.data.get('uid'), "uid")
            user_social_auth = UserSocialAuth.objects.select_related("user").filter(uid=uid).first()
            if not user_social_auth:
                raise ValueError("User does not exist with uid = {uid}".format(uid=uid))
            full_name = data.get("full_name")
            if full_name:
                request.data["name"] = full_name
            user = ytp_serializer.UserSerializer().update(user_social_auth.user, request.data)
            ytp_serializer.ProfileSerializer().update(user.profile, request.data)
        except ValueError as e:
            log.exception(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(data={"error_message": e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"user_id": user.id, "username": user.username}, status=status.HTTP_200_OK)

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
