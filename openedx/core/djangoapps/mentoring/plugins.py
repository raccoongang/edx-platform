"""
Course app configuration for mentoring.
"""
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_noop as _
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.course_apps.plugins import CourseApp

User = get_user_model()


class MentoringCourseApp(CourseApp):
    """
    Course App config for Mentoring.
    """

    app_id = "mentoring"
    name = _("Mentoring")
    description = _("Enable mentoring for your course.")
    documentation_links = {
        "learn_more_configuration": settings.MENTORING_HELP_URL,
    }

    @classmethod
    def is_available(cls, course_key: CourseKey) -> bool:
        """
        Mentoring is always available.
        """
        return True

    @classmethod
    def is_enabled(cls, course_key: CourseKey) -> bool:
        """
        Mentoring is always enabled.
        """
        return True

    @classmethod
    def get_allowed_operations(cls, course_key: CourseKey, user: Optional[User] = None) -> Dict[str, bool]:
        """
        Return allowed operations for mentoring app.
        """
        return {
            "enable": False,
            "configure": False,
        }
