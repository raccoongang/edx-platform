from django.conf import settings
from django.contrib.auth import logout
from django.http.response import HttpResponseRedirect
from django.urls import resolve, reverse


# allow access to the login page and login request
OPEN_URLS = ['login', 'login_post']


class OnlySuperuserIsAllowedMiddleware(object):
    """
    Redirect non-superusers to the login page
    """
    @staticmethod
    def process_request(request):
        url_name = resolve(request.path).url_name

        if (url_name in OPEN_URLS) or (request.user.is_authenticated and request.user.is_superuser):
            return None
        elif request.user.is_authenticated:
            # logout non-superusers if they was logged in before applying this middleware
            logout(request)

        return HttpResponseRedirect(settings.LOGIN_URL)


class UserIsActiveMiddleware(object):
    """
    Redirect non-active user to the email verification page
    """
    @property
    def allowed_urls(self):
        urls = [
            "email_verification",
            "logout",
            "activate",
        ]
        return urls

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            url_name = resolve(request.path).url_name
            if url_name not in self.allowed_urls:
                return HttpResponseRedirect(reverse('email_verification'))
