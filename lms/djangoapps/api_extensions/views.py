from django_filters import rest_framework as rf_filters
from rest_framework import status, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.lib.api.permissions import ApiKeyHeaderPermissionIsAuthenticated
from enrollment.views import ApiKeyPermissionMixIn
from lms.djangoapps.grades.models import PersistentCourseGrade
from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin
from . import filters, serializers


class CourseGradesFilterView(ReadOnlyModelViewSet, ApiKeyPermissionMixIn, DeveloperErrorViewMixin):
    permission_classes = ApiKeyHeaderPermissionIsAuthenticated,
    serializer_class = serializers.PersistentCourseGradeSerializer
    filter_class = filters.CourseGradesFilter
    filter_backends = (rf_filters.DjangoFilterBackend,)

    def list(self, request, course_id):

        # Validate course exists with provided course_id
        try:
            self.course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            raise self.api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                developer_message='The provided course key cannot be parsed.',
                error_code='invalid_course_key'
            )

        if not CourseOverview.get_from_id_if_exists(self.course_key):
            raise self.api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                developer_message="Requested grade for unknown course {course}".format(course=course_id),
                error_code='course_does_not_exist'
            )

        return super(CourseGradesFilterView, self).list(request, course_id)

    def get_queryset(self):
        persistent_course_grades = PersistentCourseGrade.objects.filter(course_id=self.course_key)
        return persistent_course_grades
