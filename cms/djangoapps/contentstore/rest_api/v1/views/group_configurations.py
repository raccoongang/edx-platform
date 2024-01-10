""" API Views for course's settings group configurations """

import edx_api_doc_tools as apidocs
from opaque_keys.edx.keys import CourseKey
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.djangoapps.contentstore.utils import get_group_configurations_context
from cms.djangoapps.contentstore.rest_api.v1.serializers import (
    CourseGroupConfigurationsSerializer,
)
from common.djangoapps.student.auth import has_studio_read_access
from openedx.core.lib.api.view_utils import (
    DeveloperErrorViewMixin,
    verify_course_exists,
    view_auth_classes,
)
from xmodule.modulestore.django import modulestore


@view_auth_classes(is_authenticated=True)
class CourseGroupConfigurationsView(DeveloperErrorViewMixin, APIView):
    """
    View for course's settings group configurations.
    """

    @apidocs.schema(
        parameters=[
            apidocs.string_parameter(
                "course_id", apidocs.ParameterLocation.PATH, description="Course ID"
            ),
        ],
        responses={
            200: CourseGroupConfigurationsSerializer,
            401: "The requester is not authenticated.",
            403: "The requester cannot access the specified course.",
            404: "The requested course does not exist.",
        },
    )
    @verify_course_exists()
    def get(self, request: Request, course_id: str):
        """
        Get an object containing course's settings group configurations.

        **Example Request**

            GET /api/contentstore/v1/group_configurations/{course_id}

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        The HTTP 200 response contains a single dict that contains keys that
        are the course's settings group configurations.

        **Example Response**

        ```json
        {
            "all_group_configurations": [
                {
                    "active": true,
                    "description": "The groups in this configuration can be mapped to cohorts in the Instructor.",
                    "groups": [
                        {
                            "id": 593758473,
                            "name": "My Content Group",
                            "usage": [],
                            "version": 1
                        }
                    ],
                    "id": 1791848226,
                    "name": "Content Groups",
                    "parameters": {},
                    "read_only": false,
                    "scheme": "cohort",
                    "version": 3
                }
            ],
            "experiment_group_configurations": null,
            "mfe_proctored_exam_settings_url": "",
            "should_show_enrollment_track": false,
            "should_show_experiment_groups": false
        }
        ```
        """
        course_key = CourseKey.from_string(course_id)
        store = modulestore()

        if not has_studio_read_access(request.user, course_key):
            self.permission_denied(request)

        with store.bulk_operations(course_key):
            course = modulestore().get_course(course_key)
            group_configurations_context = get_group_configurations_context(course, store)
            serializer = CourseGroupConfigurationsSerializer(group_configurations_context)
            return Response(serializer.data)
