class EDXSameSiteMiddleware(object):
    """
    Middleware to add a `SameSite=None` attribute to the session cookie for
    `deposit/webapp` responses. This is a work-around in-place of
    :class:`django.http.HttpResponse.set_cookie`, which does not
    allow `samesite` values of ``None``.
    Polaris developers MUST add this class to their Django app's
    ``settings.MIDDLEWARE``. Specifically, the class must be listed
    `above` :class:`django.contrib.sessions.middleware.SessionMiddleware`,
    like so:
    ::
        MIDDLEWARE = [
            'session.middleware.EDXSameSiteMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
    Fix: https://github.com/django/django/pull/11894
    Boilerplate code from:
    https://docs.djangoproject.com/en/2.2/topics/http/middleware
    """

    def process_response(self, request, response):  # pylint: disable=unused-argument
        """
        Django middleware handler to process a response
        """
        from django.conf import settings

        if settings.SESSION_COOKIE_NAME in response.cookies:
            response.cookies[settings.SESSION_COOKIE_NAME]["samesite"] = "None"
            response.cookies[settings.SESSION_COOKIE_NAME]["secure"] = True
        return response
