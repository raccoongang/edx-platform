from django.utils.translation import ugettext_noop as _

from courseware.tabs import EnrolledTab
from openedx.core.djangoapps.course_groups.cohorts import is_cohort_enabled


class CohortManagementDashboardTab(EnrolledTab):

    type = "cohort_management_dashboard"
    title = _('Cohort Management Dashboard')
    view_name = "cohort_management_dashboard:dashboard"
    is_dynamic = True

    @classmethod
    def is_enabled(cls, course, user=None):
        if is_cohort_enabled(course, user):
            return super(CohortManagementDashboardTab, cls).is_enabled(course, user)
        return False

