from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CalendarView

urlpatterns = patterns(
    'calendar_tab.views',
    url(r"^$", login_required(CalendarView.as_view()), name="calendar_view"),
)
