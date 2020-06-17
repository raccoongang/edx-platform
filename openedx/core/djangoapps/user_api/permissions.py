"""
Permissions classes for User-API aware views.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404

import third_party_auth
from openedx.core.djangoapps.user_api.accounts.api import visible_fields
from rest_framework import permissions


def is_field_shared_factory(field_name):
    """
    Generates a permission class that grants access if a particular profile field is
    shared with the requesting user.
    """

    class IsFieldShared(permissions.BasePermission):
        """
        Grants access if a particular profile field is shared with the requesting user.
        """
        def has_permission(self, request, view):
            url_username = request.parser_context.get('kwargs', {}).get('username', '')
            if request.user.username.lower() == url_username.lower():
                return True
            # Staff can always see profiles.
            if request.user.is_staff:
                return True
            # This should never return Multiple, as we don't allow case name collisions on registration.
            user = get_object_or_404(User, username__iexact=url_username)
            if field_name in visible_fields(user.profile, user):
                return True
            raise Http404()

    return IsFieldShared


class CanRegisterAccount(permissions.IsAuthenticated):
    """
    Check access to register new account.
    It's allowed to access RegistrationView if:
        - request.method != 'POST';
        - request referer is the platform '/register' page
        - request to register using third party auth (Google, Facebook, etc.)
        - requesting user has jwt-token (for API calls)
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        if request.META.get('HTTP_REFERER') == request.build_absolute_uri(reverse('register_user')):
            return True
        if third_party_auth.is_enabled():
            if third_party_auth.pipeline.running(request):
                return True
            elif request.POST.get('provider') or request.POST.get('social_auth_provider'):
                return True
        return permissions.IsAuthenticated.has_permission(self, request, view)
