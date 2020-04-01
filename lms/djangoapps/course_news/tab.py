"""
Course news tab.
"""

from django.conf import settings
from django.utils.translation import ugettext_noop

from courseware.tabs import EnrolledTab
from xmodule.tabs import TabFragmentViewMixin


class NewsTab(TabFragmentViewMixin, EnrolledTab):
    """
    Defines the News view type that is shown as a course tab.
    """
    type = "news"
    title = ugettext_noop('News')
    view_name = "course_news_view"
    fragment_view_name = 'course_news.views.CourseNewsFragmentView'
    is_hideable = False

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Returns true if the news is enabled and the specified user is enrolled or has staff access.
        """
        if not super(NewsTab, cls).is_enabled(course, user):
            return False
        return settings.NEWS_ENABLED
