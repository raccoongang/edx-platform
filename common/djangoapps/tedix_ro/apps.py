from django.apps import AppConfig


class TedixRoConfig(AppConfig):
    """
    Application Configuration for tedix_ro.
    """
    name = 'tedix_ro'

    def ready(self):
        """
        Connect signal handlers.
        """
        from . import signals  # pylint: disable=unused-variable
