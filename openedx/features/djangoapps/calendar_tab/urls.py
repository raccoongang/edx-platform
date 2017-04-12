from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import calendar_view

urlpatterns = patterns(
    'calendar_tab.views',
    url(r"^/$", login_required(calendar_view), name="calendar_view")
)
