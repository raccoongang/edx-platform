"""
API v0 views.
"""
from django.shortcuts import get_object_or_404

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.locator import LibraryLocatorV2
from openedx_learning.api.authoring_models import DraftChangeLog
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.djangoapps.import_from_modulestore.api import import_course_to_library
from cms.djangoapps.import_from_modulestore.models import Import
from cms.djangoapps.import_from_modulestore.permissions import IsImportAuthor
from cms.djangoapps.import_from_modulestore.views.v0.serializers import (
  CreateImportTaskSerializer,
  ImportTaskStatusSerializer,
)
from openedx.core.djangoapps.content_libraries.api import ContentLibrary
from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser


class ImportView(APIView):
    """
    Import course content from modulestore into a content library.
    """

    permission_classes = (IsAdminUser, IsImportAuthor)
    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    serializer_class = ImportTaskStatusSerializer
    method_serializers = {
      'GET': ImportTaskStatusSerializer,
      'POST': CreateImportTaskSerializer,
    }

    def get_serializer_class(self):
        """
        Return the serializer class for the import task based on the request method.
        """
        return self.method_serializers.get(self.request.method, self.serializer_class)

    def post(self, request, *args, **kwargs):
        """
        Handle the import task creation.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        target_change = DraftChangeLog.objects.filter(learning_package__key=validated_data['target']).last()
        library_key = LibraryLocatorV2.from_string(validated_data['target'])
        learning_package_id = ContentLibrary.objects.get(
          org__short_name=library_key.org, slug=library_key.slug
        ).learning_package_id

        import_course_to_library(
          source_key=validated_data['source_key'],
          target_change_id=target_change.id,
          user_id=request.user.pk,
          usage_ids=validated_data['usage_keys_string'],
          learning_package_id=learning_package_id,
          composition_level=validated_data['composition_level'],
          override=validated_data['override'],
        )
        return Response("Import created successfully", status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Handle the import task status retrieval.
        """
        import_instance = get_object_or_404(Import, status__uuid=kwargs['uuid'])
        serializer = self.get_serializer_class()(import_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
