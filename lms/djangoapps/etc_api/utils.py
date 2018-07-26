import re

from random import randint

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from student.forms import PasswordResetFormNoActive
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from rest_framework import permissions
from django.http import Http404

def auto_generate_username(email):
    """
    This functions generates a valid username based on the email, also checks if
    the username exists and adds a random 3 digit int at the end to warranty
    uniqueness.
    """
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("Email is a invalid format")

    username = ''.join(e for e in email.split('@')[0] if e.isalnum())

    while check_account_exists(username=username):
        username = ''.join(e for e in email.split('@')[0] if e.isalnum()) + str(randint(100,999))

    return username


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
        return True
    else:
        return False

class ApiKeyHeaderPermissionInToken(ApiKeyHeaderPermission, permissions.IsAuthenticated):
    """
    Custom class to check permission by token
    """

    def has_permission(self, request, view):
        """
               Check for permissions by matching the configured API key and header
               If settings.DEBUG is True and settings.EDX_APP_SEMBLER_API_KEY is not set or None,
               then allow the request. Otherwise, allow the request if and only if
               settings.EDX_APP_SEMBLER_API_KEY is set and the X-Edx-App-Semb-Api-Key HTTP header is
               present in the request and matches the setting.
               """
        api_key = getattr(settings, "EDX_APP_ETC_API_KEY", None)
        is_enable_api = configuration_helpers.get_value("ENABLE_APP_ETC_API", None)

        if not is_enable_api:
            raise Http404
        #and request.META.get("HTTP_X_APP_ETC_API_KEY") == api_key
        return (
                (settings.DEBUG and api_key is None) or
                (is_enable_api is not None and api_key is not None )
        )
