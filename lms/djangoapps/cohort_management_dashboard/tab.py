from django.utils.translation import ugettext_noop

from courseware.tabs import EnrolledTab

class CohortManagementDashboardTab(EnrolledTab):

    type = "cohort_management_dashboard"
    title = 'Cohort Management Dashboard'
    view_name = "cohort_management_dashboard:dashboard"
    is_dynamic = True

    @classmethod
    def is_enabled(cls, course, user=None):
        return super(CohortManagementDashboardTab, cls).is_enabled(course, user)

