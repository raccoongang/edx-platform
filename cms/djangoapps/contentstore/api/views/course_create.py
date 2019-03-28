from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin

from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from ..serializers.course_create import CourseCreateSerializer


class CourseCreateView(CreateModelMixin, GenericAPIView):
    permission_classes = (ApiKeyHeaderPermission,)
    serializer_class = CourseCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
