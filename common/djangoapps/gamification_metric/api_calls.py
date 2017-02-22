"""
Send user's achievements to external service during the course progress
"""
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class APICalls(object):
    """
    Send user data to the Gamification server
    """

    def __init__(self):
        self.is_enabled = settings.FEATURES.get('ENABLE_GAMMA', False)
        if self.is_enabled:
            self.GAMMA_PROPERTIES = settings.FEATURES.get('GAMMA_PROPERTIES', {})
            if not self.GAMMA_PROPERTIES:
                raise ImproperlyConfigured(
                    "You must set `GAMMA_PROPERTIES` when "
                    "`FEATURES['ENABLE_GAMMA']` is True."
                )
            required_params = ("API_URL", "APP_KEY", "APP_SECRET")
            for param in required_params:
                if param not in self.GAMMA_PROPERTIES:
                    raise ImproperlyConfigured(
                        "You must set `{}` in `GAMMA_PROPERTIES`".format(param)
                    )

    def api_call(self, course_id, org, username, event_type, uid):
        data = {
            'course_id': course_id,
            'org': org,
            'username': username,
            'event_type': event_type,
            'uid': uid,
        }
        headers = {
            'App-key': self.GAMMA_PROPERTIES['APP_KEY'],
            'App-secret': self.GAMMA_PROPERTIES['APP_SECRET']
        }
        requests.put(
            self.GAMMA_PROPERTIES['API_URL']+'gamma-profile/',
            data=data,
            headers=headers,
            verify=False
        )
