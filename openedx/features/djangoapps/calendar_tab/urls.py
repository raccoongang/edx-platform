from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CalendarView, InitCalendarView, events_view, dataprocessor_view

urlpatterns = patterns(
    'calendar_tab.views',
    url(r"^$", login_required(CalendarView.as_view()), name="calendar_view"),
    url(r"^init/$", login_required(InitCalendarView.as_view()), name="calendar_init"),
    url(r"^events/$", events_view, name="events_view"),
    url(r"^dataprocessor/$", dataprocessor_view, name="dataprocessor"),
)
