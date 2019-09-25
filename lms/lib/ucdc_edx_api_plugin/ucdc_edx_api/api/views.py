import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from student.models import UserProfile
from third_party_auth.models import OAuth2ProviderConfig
from ucdc_edx_api.api.permissions import AnonPermissionOnly
from ucdc_edx_api.api.serializers import UserRegisterSerializer, UserSocialAuthSerializer

log = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission, AnonPermissionOnly)

    def post(self, request, *args, **kwargs):
        params = request.data.copy()
        user_serializer = UserRegisterSerializer(data=params)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
        UserProfile.objects.create(user=user, allow_certificate=True)
        # NOTE: Expects that OAuth2ProviderConfig should be only one at database level at all.
        # Now it configures only manually from django admin panel.
        params["provider"] = OAuth2ProviderConfig.objects.first().backend_name
        social_auth_serializer = UserSocialAuthSerializer(data=params)
        if social_auth_serializer.is_valid(raise_exception=True):
            social_auth_serializer.save(user=user)
        log.info("User %s was created. Email: %s. UID: %s", params["username"], params["email"], params["uid"])

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
