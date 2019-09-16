"""
Cohort management dashboard.
"""
from django.apps import AppConfig

from openedx.core.constants import COURSE_ID_PATTERN
from openedx.core.djangoapps.plugins.constants import ProjectType, PluginURLs


class CohortManagementDashboardApp(AppConfig):
    """
    Application configuration for Cohort Management Dashboard.
    """
    name = u'lms.djangoapps.cohort_management_dashboard'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'cohort_management_dashboard',
                PluginURLs.REGEX: u'courses/{}/cohort/'.format(COURSE_ID_PATTERN),
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        }
    }
