from django.utils.translation import ugettext_noop

from courseware.tabs import EnrolledTab
from xmodule.tabs import TabFragmentViewMixin


class CalendarTab(TabFragmentViewMixin, EnrolledTab):
    """
    Navigation tab to operate with google calendar of the course.
    """
    name = "calendar"
    tab_id = "calendar"

    type = "calendar"
    title = ugettext_noop("Calendar")
    body_class = "calendar-tab"
    is_hideable = True
    is_default = True

    # view_name = "calendar_tab.views.calendar_view"
    fragment_view_name = 'openedx.features.calendar_tab.views.CalendarTabFragmentView'

    @classmethod
    def is_enabled(cls, course, user=None):
        return True
