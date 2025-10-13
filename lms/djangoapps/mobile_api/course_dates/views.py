"""
API views for course dates.
"""

from django.contrib.auth.models import User  # lint-amnesty, pylint: disable=imported-auth-user
from django.shortcuts import get_object_or_404
from django.utils import timezone
from edx_when.api import _are_relative_dates_enabled
from edx_when.models import UserDate
from rest_framework import views
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from xmodule.modulestore.django import modulestore

from ..decorators import mobile_view
from .serializers import AllCourseDatesSerializer


class AllCourseDatesPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


@mobile_view()
class AllCourseDatesAPIView(views.APIView):
    """
    API for retrieving all course dates for a specific user.
    This view provides a list of course dates for a user, including due dates for
    assignments and other course content.
    **Example Request**
        GET /api/mobile/{api_version}/course_dates/<user_name>/
    **Example Response**
        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
            {
                "course_id": "course-v1:1+1+1",
                "due_date": "2030-01-01T00:00:00+0000",
                "assignment_title": "Subsection name",
                "learner_has_access": true,
                "course_name": "Course name",
                "relative": false,
                "location": "course-v1:AAA+BBB+2030",
                "first_component_block_id": ""
            },
            {
                "course_id": "course-v1:1+1+1",
                "due_date": "2030-01-01T00:00:00+0000",
                "assignment_title": "Subsection name",
                "learner_has_access": true,
                "course_name": "Course name",
                "relative": true,
                "location": "course-v1:AAA+BBB+2030",
                "first_component_block_id": ""
            },
        }
        ```
    """

    pagination_class = AllCourseDatesPagination

    def get(self, request, *args, **kwargs) -> Response:
        user = get_object_or_404(User, username=kwargs.get("username"))
        user_dates = UserDate.objects.filter(user=user).select_related("content_date", "content_date__policy")
        now = timezone.now()

        user_dates_filtered = []
        for user_date in user_dates:
            is_date_in_future = user_date.actual_date > now

            is_date_relative = user_date.rel_date is not None or user_date.content_date.policy.rel_date is not None
            course_id = user_date.content_date.course_id
            course = modulestore().get_course(course_id)
            is_course_relative = all(
                [course.self_paced, _are_relative_dates_enabled(course_id), bool(course.relative_weeks_due)]
            )

            if is_date_in_future or (is_date_relative and is_course_relative):
                user_dates_filtered.append(user_date)

        user_dates_sorted = sorted(user_dates_filtered, key=lambda ud: ud.actual_date)

        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(user_dates_sorted, request)
        serializer = AllCourseDatesSerializer(paginated_data, many=True)

        return paginator.get_paginated_response(serializer.data)
