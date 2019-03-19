""" Course Import API URLs. """
from django.conf import settings
from django.conf.urls import (
    patterns,
    url,
)

from cms.djangoapps.contentstore.api import views

urlpatterns = patterns(
    '',
    url(r'^v0/check_rerun_courses/$', views.check_rerun_courses, name='check_rerun_courses'),
)
