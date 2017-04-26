from django.utils.translation import ugettext_noop
from courseware.tabs import CourseTab
from django.conf import settings


class CalendarTab(CourseTab):
    """
    Navigation tab to operate with google calendar of the course.
    """
    type = "calendar"
    name = "calendar"
    title = ugettext_noop("Calendar")
    view_name = "calendar_view"
    is_default = True
    is_hideable = True
    is_hidden = True
    tab_id = "calendar"

    @classmethod
    def is_enabled(cls, course, user=None):
        return settings.FEATURES.get('ENABLE_CALENDAR', False)
