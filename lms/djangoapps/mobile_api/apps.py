"""
Configuration for the mobile_api Django application.
"""


from django.apps import AppConfig


class MobileApiConfig(AppConfig):
    """
    Configuration class for the mobile_api Django application.
    """
    name = 'lms.djangoapps.mobile_api'
    verbose_name = "Mobile API"

    def ready(self):
        """
        Connect signal handlers.
        """
        from lms.djangoapps.mobile_api.offline_mode import signals  # pylint: disable=unused-import
        from lms.djangoapps.mobile_api.offline_mode import tasks    # pylint: disable=unused-import
