"""
Tests for the tasks module in import_from_modulestore.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from openedx_learning.api.authoring_models import LearningPackage
from user_tasks.models import UserTaskStatus
from common.djangoapps.student.tests.factories import UserFactory
from ..constants import IMPORT_FROM_MODULESTORE_PURPOSE
from ..data import ImportStatus
from ..models import Import
from ..tasks import ImportCourseTask, import_course_to_library_task


class TestImportCourseTask(TestCase):
    """
    Tests for the ImportCourseTask class.
    """

    def test_calculate_total_steps(self):
        """
        Test that calculate_total_steps returns 2 (for staging and importing).
        """
        result = ImportCourseTask.calculate_total_steps({})
        self.assertEqual(result, 2)

    def test_generate_name(self):
        """
        Test that generate_name correctly formats the task name.
        """
        arguments = {
            'learning_package_id': 123,
            'import_pk': 456,
        }
        expected_name = 'Import course to library (library_id=123, import_id=456)'
        result = ImportCourseTask.generate_name(arguments)
        self.assertEqual(result, expected_name)


class TestImportCourseToLibraryTask(TestCase):
    """
    Tests for the import_course_to_library_task function.
    """
    def setUp(self):
        """Set up common test data."""
        self.user = UserFactory(is_staff=True, is_superuser=True)
        self.import_obj = Import.objects.create(
            source_key='course-v1:edX+DemoX+Demo_Course',
            user=self.user,
        )
        self.usage_keys_string = ['block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_test']
        self.learning_package_id = 456
        self.composition_level = 'component'
        self.override = False

    @patch('cms.djangoapps.import_from_modulestore.tasks.Import.objects.get')
    def test_import_not_found(self, mock_import_get):
        """Test behavior when Import doesn't exist."""
        mock_import_get.side_effect = Import.DoesNotExist

        import_course_to_library_task.delay(
            self.import_obj.pk, self.usage_keys_string, self.learning_package_id,
            self.user.pk, self.composition_level, self.override
        )

        mock_import_get.assert_called_once_with(pk=self.import_obj.pk, user_id=self.user.pk)

    def test_user_task_status_created(self):
        """Test that UserTaskStatus is created."""
        import_course_to_library_task.delay(
            self.import_obj.pk, self.usage_keys_string, self.learning_package_id,
            self.user.pk, self.composition_level, self.override
        )

        self.import_obj.refresh_from_db()
        self.assertIsInstance(self.import_obj.status, UserTaskStatus)
