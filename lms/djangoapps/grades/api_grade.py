import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


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
            required_params = ("API_URL", "APP_KEY", "APP_SECRET")
            for param in required_params:
                if param not in self.API_GRADE_PROPERTIES:
                    raise ImproperlyConfigured(
                        "You must set `{}` in `API_GRADE_PROPERTIES`".format(param)
                    )

    def api_call(self, contentProvider, userId, courseId, lastlogin, percentageOfcompletion, duration,
            lastVisit, completationDate, studentGrade, main_topic, skilltag, course_level, effort):
        data = {
            "contentProvider": contentProvider,
            "userid": userId,
            "courseId": courseId,
            "lastlogin": lastlogin,
            "percentageOfcompletion": percentageOfcompletion,
            "duration":duration,
            "lastVisit": lastVisit,
            "completationDate" : completationDate,
            "studentGrade": studentGrade,
            "main_topic": main_topic,
            "skilltag": skilltag,
            "course_level": course_level,
            "effort": effort
        }
        headers = {
            'x-functions-key': self.API_GRADE_PROPERTIES['APP_KEY'],
        }
        requests.post(
            '{api_url}/orchestrators/feedbackloop/{userId}}/?code={secret}'.format(
                api_url=self.API_GRADE_PROPERTIES['API_URL'],
                userId=userId,
                secret=self.API_GRADE_PROPERTIES['APP_SECRET']
            ),
            data=data,
            headers=headers,
            #verify=False
        )
