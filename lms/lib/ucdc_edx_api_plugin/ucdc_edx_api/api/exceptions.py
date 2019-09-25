from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ResourceConflicts(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(
        "Request could not be completed due to a conflict with the current state of the target resource."
    )
    default_code = "resource_conflict"


class UserSocialOAuthMisconfiguration(Exception):
    pass
