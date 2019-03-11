import logging
import requests
import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

log = logging.getLogger(__name__)


class APIGrade(object):
    """
    Send user data to the Gamification server
    """
    def __init__(self):
        self.is_enabled = settings.FEATURES.get('ENABLE_API_GRADE', False)
        if self.is_enabled:
            self.API_GRADE_PROPERTIES = settings.FEATURES.get('API_GRADE_PROPERTIES', {})
            if not self.API_GRADE_PROPERTIES:
                raise ImproperlyConfigured(
                    "You must set `API_GRADE_PROPERTIES` when "
                    "`FEATURES['ENABLE_API_GRADE']` is True."
                )
            required_params = ("API_URL", "APP_SECRET", "APP_CLIENT_ID")
            for param in required_params:
                if not self.API_GRADE_PROPERTIES.get(param) or param not in self.API_GRADE_PROPERTIES:
                    raise ImproperlyConfigured(
                        "You must set `{}` in `API_GRADE_PROPERTIES`".format(param)
                    )

    def api_call(self, contentProvider, user, courseId, lastlogin, percentageOfcompletion, duration,
            lastVisit, completationDate, studentGrade, main_topic, skilltag, course_level, effort):
        if self.is_enabled:
            data = {
                "contentProvider": contentProvider,
                "user": user.email,
                "courseId": courseId,
                "lastlogin": lastlogin,
                "percentageOfcompletion": percentageOfcompletion,
                "duration": duration,
                "lastVisit": lastVisit,
                "completationDate" : completationDate,
                "studentGrade": studentGrade,
                "main_topic": main_topic,
                "skilltag": skilltag,
                "course_level": course_level,
                "effort": effort
            }
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
            }
            response = requests.post(
                'https://{api_url}/api/orchestrators/feedbackloop/{userId}?code={secret}==&clientId={client_id}'.format(
                    api_url=self.API_GRADE_PROPERTIES['API_URL'],
                    userId=user.id,
                    secret=self.API_GRADE_PROPERTIES['APP_SECRET'],
                    client_id=self.API_GRADE_PROPERTIES['APP_CLIENT_ID'],
                ),
                data=json.dumps(data),
                headers=headers
            )
            if response.status_code == 200:
                log.info('Data "{}" has been successfully sent'.format(data))
            else:
                log.error('Error while sending data "{}", status code - {}, message - "{}"'.format(data, response.status_code, response.content))
