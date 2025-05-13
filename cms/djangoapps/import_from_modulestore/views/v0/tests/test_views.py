"""
Tests for Import views (v0).
"""
import uuid
from unittest import mock
from django.contrib.auth.models import User
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.locator import LibraryLocatorV2
from openedx_learning.api.authoring_models import DraftChangeLog, LearningPackage
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from cms.djangoapps.import_from_modulestore.models import Import, ImportStatus
from cms.djangoapps.import_from_modulestore.permissions import IsImportAuthor
from cms.djangoapps.import_from_modulestore.views.v0.views import ImportView
from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
from rest_framework.permissions import IsAdminUser

from cms.djangoapps.import_from_modulestore.views.v0.serializers import (
    CreateImportTaskSerializer,
    ImportTaskStatusSerializer,
)


class TestImportView(APITestCase):
    """
    Tests for the ImportView.
    """
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_superuser(username='testuser', email='test@example.com', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.import_uuid = str(uuid.uuid4())
        self.import_status = mock.MagicMock(spec=ImportStatus)
        self.import_status.uuid = self.import_uuid
        self.import_status.created = '2023-10-01T00:00:00Z'
        self.import_status.state = 'pending'
        self.import_status.name = 'Import Task'

        self.import_instance = mock.MagicMock(spec=Import)
        self.import_instance.status = self.import_status

        self.valid_post_data = {
            'source_key': 'course-v1:edX+DemoX+Demo_Course',
            'target': 'lib:edX:library1',
            'usage_keys_string': 'block-v1:edX+DemoX+Demo_Course+type@html+block@12345',
            'composition_level': 'unit',
            'override': True
        }

        self.learning_package = mock.MagicMock(spec=LearningPackage)
        self.learning_package.key = 'lib:edX:library1'
        self.learning_package_id = 1

        self.draft_change = mock.MagicMock(spec=DraftChangeLog)
        self.draft_change.id = 100
        self.draft_change.learning_package = self.learning_package

        self.library_key = mock.MagicMock(spec=LibraryLocatorV2)
        self.library_key.org = 'edX'
        self.library_key.slug = 'library1'

        self.content_library = mock.MagicMock()
        self.content_library.learning_package_id = self.learning_package_id

    def test_authentication_classes(self):
        """Test that the view has the expected authentication classes."""
        self.assertEqual(
            ImportView.authentication_classes,
            (
                JwtAuthentication,
                BearerAuthenticationAllowInactiveUser,
                SessionAuthenticationAllowInactiveUser,
            )
        )

    def test_permission_classes(self):
        """Test that the view has the expected permission classes."""
        self.assertEqual(
            ImportView.permission_classes,
            (IsAdminUser, IsImportAuthor)
        )

    def test_get_serializer_class_for_get(self):
        """Test that the correct serializer is returned for GET requests."""
        view = ImportView()
        request = self.factory.get('/path/')
        view.request = Request(request)
        self.assertEqual(view.get_serializer_class(), ImportTaskStatusSerializer)

    def test_get_serializer_class_for_post(self):
        """Test that the correct serializer is returned for POST requests."""
        view = ImportView()
        request = self.factory.post('/path/')
        view.request = Request(request)
        self.assertEqual(view.get_serializer_class(), CreateImportTaskSerializer)

    @mock.patch('cms.djangoapps.import_from_modulestore.views.v0.views.DraftChangeLog.objects.filter')
    @mock.patch('cms.djangoapps.import_from_modulestore.views.v0.views.LibraryLocatorV2.from_string')
    @mock.patch('cms.djangoapps.import_from_modulestore.views.v0.views.ContentLibrary.objects.get')
    @mock.patch('cms.djangoapps.import_from_modulestore.views.v0.views.import_course_to_library')
    def test_post_import_task(self, mock_import, mock_content_lib_get, mock_lib_from_string, mock_draft_filter):
        """Test creating a new import task."""
        mock_draft_queryset = mock.MagicMock()
        mock_draft_queryset.last.return_value = self.draft_change
        mock_draft_filter.return_value = mock_draft_queryset
        
        mock_lib_from_string.return_value = self.library_key
        mock_content_lib_get.return_value = self.content_library
        mock_import.return_value = self.import_instance

        request = self.factory.post('/api/import_from_modulestore/v0/import/', data=self.valid_post_data, format='json')
        request.user = self.user
        
        view = ImportView()
        view.request = request
        view.format_kwarg = None

        request = view.initialize_request(request)
        view.request = request

        with mock.patch('cms.djangoapps.import_from_modulestore.views.v0.serializers.CreateImportTaskSerializer.is_valid') as mock_is_valid:
            mock_is_valid.return_value = True
            with mock.patch('cms.djangoapps.import_from_modulestore.views.v0.serializers.CreateImportTaskSerializer.validated_data', 
                           new_callable=mock.PropertyMock) as mock_validated_data:
                mock_validated_data.return_value = self.valid_post_data
                response = view.post(request)

        mock_draft_filter.assert_called_once_with(learning_package__key=self.valid_post_data['target'])
        mock_lib_from_string.assert_called_once_with(self.valid_post_data['target'])
        mock_content_lib_get.assert_called_once_with(
            org__short_name=self.library_key.org, 
            slug=self.library_key.slug
        )
        mock_import.assert_called_once_with(
            source_key=self.valid_post_data['source_key'],
            target_change_id=self.draft_change.id,
            user_id=self.user.pk,
            usage_ids=self.valid_post_data['usage_keys_string'],
            learning_package_id=self.learning_package_id,
            composition_level=self.valid_post_data['composition_level'],
            override=self.valid_post_data['override'],
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('cms.djangoapps.import_from_modulestore.views.v0.views.get_object_or_404')
    def test_get_import_status(self, mock_get_object):
        """Test retrieving import task status."""
        mock_get_object.return_value = self.import_instance

        request = self.factory.get(f'/api/import_from_modulestore/v0/import/{self.import_uuid}/')
        request.user = self.user

        view = ImportView()
        view.request = request
        view.format_kwarg = None

        with mock.patch('cms.djangoapps.import_from_modulestore.views.v0.serializers.ImportTaskStatusSerializer.__call__') as mock_serializer:
            mock_serializer.return_value.data = {'status': 'success'}
            response = view.get(request, uuid=self.import_uuid)

        mock_get_object.assert_called_once_with(Import, status__uuid=self.import_uuid)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_import_task_validation_error(self):
        """Test error handling for invalid import task data."""
        request = self.factory.post('/api/import_from_modulestore/v0/import/', data=self.valid_post_data, format='json')
        request.user = self.user

        view = ImportView()
        view.request = request
        view.format_kwarg = None

        request = view.initialize_request(request)
        view.request = request

        with mock.patch('cms.djangoapps.import_from_modulestore.views.v0.serializers.CreateImportTaskSerializer.is_valid') as mock_is_valid:
            mock_is_valid.side_effect = ValidationError("Invalid data")
            with self.assertRaises(ValidationError):
                view.post(request)
