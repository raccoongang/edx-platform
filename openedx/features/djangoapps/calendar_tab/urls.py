from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CalendarView, InitCalendarView

urlpatterns = patterns(
    'calendar_tab.views',
    url(r"^$", login_required(CalendarView.as_view()), name="calendar_view"),
    url(r"^init$", login_required(InitCalendarView.as_view()), name="calendar_init"),
)
