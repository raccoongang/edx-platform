"""
URLs for mentoring AI API
"""

from django.conf import settings
from django.urls import re_path

from .api_views import CourseAIContextAPIView

urlpatterns = [
    re_path(
        r"^context/{course_id}$".format(course_id=settings.COURSE_ID_PATTERN),
        CourseAIContextAPIView.as_view(),
        name="course-ai-context",
    ),
]
