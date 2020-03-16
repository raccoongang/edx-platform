"""
Hera Application Configuration
"""

from django.apps import AppConfig


class HeraConfig(AppConfig):
    name = 'hera'

    def ready(self):
        from . import signals
