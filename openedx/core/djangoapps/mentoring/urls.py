"""
URLs for mentoring apps
"""

from django.urls import include, path

urlpatterns = [
    path("ai/", include("openedx.core.djangoapps.mentoring.ai.urls")),
]
