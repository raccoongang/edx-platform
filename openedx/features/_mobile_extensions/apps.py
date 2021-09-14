import logging

from django.apps import AppConfig


log = logging.getLogger(__name__)


class MobileExtensionsConfig(AppConfig):
    name = 'openedx.features._mobile_extensions'
    verbose_name = 'Mobile Extensions'

    def ready(self):
        # Import signals to activate signal handler
        from . import signals  # pylint: disable=unused-variable
