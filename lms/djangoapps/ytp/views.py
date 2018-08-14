from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermissionIsAuthenticated
from rest_framework.views import APIView

from certificates.views import search_certificates
from enrollment.views import ApiKeyPermissionMixIn


class SearchCertificatesView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermissionIsAuthenticated,)

    def get(self, request):
        return search_certificates(request)
