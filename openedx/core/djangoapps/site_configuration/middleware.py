"""
This file contains Django middleware related to the site_configuration app.
"""

from django.conf import settings
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect

class SessionCookieDomainOverrideMiddleware(object):
    """
    Special case middleware which should be at the very end of the MIDDLEWARE list (so that it runs first
    on the process_response chain). This middleware will define a wrapper function for the set_cookie() function
    on the HttpResponse object, if the request is running in a middleware.

    This wrapped set_cookie will change the SESSION_COOKIE_DOMAIN setting so that the cookie can be bound to a
    fully customized URL.
    """

    def process_response(self, __, response):
        """
        Django middleware hook for process responses
        """

        # Check for SESSION_COOKIE_DOMAIN setting override
        session_cookie_domain = configuration_helpers.get_value('SESSION_COOKIE_DOMAIN')
        if session_cookie_domain:
            def _set_cookie_wrapper(key, value='', max_age=None, expires=None, path='/', domain=None, secure=None,
                                    httponly=False):
                """
                Wrapper function for set_cookie() which applies SESSION_COOKIE_DOMAIN override
                """

                # only override if we are setting the cookie name to be the one the Django Session Middleware uses
                # as defined in settings.SESSION_COOKIE_NAME
                if key == configuration_helpers.get_value('SESSION_COOKIE_NAME', settings.SESSION_COOKIE_NAME):
                    domain = session_cookie_domain

                # then call down into the normal Django set_cookie method
                return response.set_cookie_wrapped_func(
                    key,
                    value,
                    max_age=max_age,
                    expires=expires,
                    path=path,
                    domain=domain,
                    secure=secure,
                    httponly=httponly
                )

            # then point the HttpResponse.set_cookie to point to the wrapper and keep
            # the original around
            response.set_cookie_wrapped_func = response.set_cookie
            response.set_cookie = _set_cookie_wrapper

        return response


class AuthorizationCheckMiddleware(object):
    """
    Middleware for checking the authorization of users.

    If not authorized and  site's setting 'DISABLE_CHECK_AUTHORIZATION' is False
    then redirects to the authorization page.
    Administrator page exceptions.
    """

    def process_request(self, request):
        """
        Django middleware hook for process request
        """
        if (
                not configuration_helpers.get_value('DISABLE_CHECK_AUTHORIZATION', False) and
                request.method == 'GET' and
                not request.user.is_authenticated() and
                '/admin' not in request.get_full_path() and
                'signin_user' != resolve(request.path).url_name

        ):
            return HttpResponseRedirect(reverse('signin_user'))
