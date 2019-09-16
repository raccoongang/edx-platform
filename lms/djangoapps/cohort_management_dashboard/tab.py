from django.utils.translation import ugettext_noop as _

from courseware.access import has_access
from courseware.tabs import EnrolledTab
from openedx.core.djangoapps.course_groups.cohorts import is_course_cohorted

class CohortManagementDashboardTab(EnrolledTab):

    type = "cohort_management_dashboard"
    title = _('Cohort Management Dashboard')
    view_name = "cohort_management_dashboard:dashboard"
    is_dynamic = True

    @classmethod
    def is_enabled(cls, course, user=None):
        if (
            (has_access(user, 'staff', course, course.id) or has_access(user, 'instructor', course, course.id)
            or user.is_staff or user.is_superuser) and is_course_cohorted(course.id)
        ):
            return super(CohortManagementDashboardTab, cls).is_enabled(course, user)
        return False

