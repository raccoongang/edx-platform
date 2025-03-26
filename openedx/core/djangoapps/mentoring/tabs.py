from django.utils.translation import gettext as _

from openedx.features.course_experience.url_helpers import get_learning_mfe_home_url
from lms.djangoapps.courseware.tabs import EnrolledTab


class MentoringTab(EnrolledTab):
    """
    A tab representing the mentoring apps for a course.
    """
    type = "mentoring"
    title = _("Mentoring")
    priority = 30
    is_dynamic = True
    view_name = "mentoring"

    def __init__(self, tab_dict):
        def link_func(course, _reverse_func):
            return get_learning_mfe_home_url(course_key=course.id, url_fragment='mentoring')

        tab_dict['link_func'] = link_func
        super().__init__(tab_dict)

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Return whether the mentoring tab is enabled for the course.
        """
        return True
