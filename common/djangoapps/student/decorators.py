"""
Decorators for help checking data
"""
import urllib
import urllib2
import json
from functools import wraps
from django.conf import settings


def check_recaptcha(view_func):
    """
    Check recaptcha.
    Forms shoud contain the following:
    <script src='https://www.google.com/recaptcha/api.js'></script>
    <div class="g-recaptcha" data-sitekey="{GOOGLE_RECAPTCHA_DATA_SITE_KEY}"></div>
    This decorator use settings.GOOGLE_RECAPTCHA_SECRET_KEY, settings.USE_GOOGLE_RECAPTCHA (True/false) and Post parameter 'g-recaptcha-response'
    for check recaptcha and write to request next parameter:
    'recaptcha_is_valid = True/False'
    If reCapcha is False write messages.error.
    For use add decorator to view function and write check parameters 'request.recaptcha_is_valid'
    More:
    https://developers.google.com/recaptcha/
    https://developers.google.com/recaptcha/docs/verify
    :param view_func:
    :return:
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST' and settings.USE_GOOGLE_RECAPTCHA:
            # Begin reCAPTCHA validation
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            result = json.load(response)
            # End reCAPTCHA validation
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False

        return view_func(request, *args, **kwargs)

    return _wrapped_view