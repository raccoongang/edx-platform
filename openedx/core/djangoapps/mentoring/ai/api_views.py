"""
API views for mentoring AI.
"""

from rest_framework import views
from rest_framework.response import Response

from .utils import get_course_structure


class CourseAIContextAPIView(views.APIView):
    def get(self, request, *args, **kwargs) -> Response:
        course_structure = get_course_structure(kwargs.get("course_id"))

        return Response(course_structure)
