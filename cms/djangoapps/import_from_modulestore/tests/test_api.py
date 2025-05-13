"""
Tests for import_from_modulestore API.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..api import import_course_to_library


class TestImportCourseToLibrary(TestCase):
    """
    Tests for import_course_to_library API.
    """

    def setUp(self):
        """
        Set up common test data.
        """
        self.source_key = "source:key"
        self.target_change_id = 1
        self.user_id = 2
        self.usage_ids = ["usage:id1", "usage:id2"]
        self.learning_package_id = 3
        self.composition_level = "unit"
        self.override = False

    @patch('cms.djangoapps.import_from_modulestore.api.validate_composition_level')
    @patch('cms.djangoapps.import_from_modulestore.api.validate_usage_keys_to_import')
    @patch('cms.djangoapps.import_from_modulestore.api._Import.objects.create')
    @patch('cms.djangoapps.import_from_modulestore.api.import_course_to_library_task.delay')
    def test_import_course_to_library(
        self,
        mock_task_delay,
        mock_create,
        mock_validate_usage_keys,
        mock_validate_composition_level
    ):
        """
        Test that import_course_to_library calls the right functions with the right parameters.
        """
        mock_import = MagicMock()
        mock_import.pk = 4
        mock_create.return_value = mock_import

        result = import_course_to_library(
            self.source_key,
            self.target_change_id,
            self.user_id,
            self.usage_ids,
            self.learning_package_id,
            self.composition_level,
            self.override
        )

        mock_validate_composition_level.assert_called_once_with(self.composition_level)
        mock_validate_usage_keys.assert_called_once_with(self.usage_ids)

        mock_create.assert_called_once_with(
            source_key=self.source_key,
            target_change_id=self.target_change_id,
            user_id=self.user_id
        )

        mock_task_delay.assert_called_once_with(
            import_pk=str(mock_import.pk),
            usage_keys_string=self.usage_ids,
            learning_package_id=self.learning_package_id,
            user_id=self.user_id,
            composition_level=self.composition_level,
            override=self.override
        )

        self.assertEqual(result, mock_import)

    @patch('cms.djangoapps.import_from_modulestore.api.validate_composition_level')
    @patch('cms.djangoapps.import_from_modulestore.api.validate_usage_keys_to_import')
    def test_import_course_to_library_validation_error(
        self,
        mock_validate_usage_keys,
        mock_validate_composition_level
    ):
        """
        Test that validation errors are raised when invalid parameters are provided.
        """
        mock_validate_composition_level.side_effect = ValueError("Invalid composition level")

        with self.assertRaises(ValueError):
            import_course_to_library(
                self.source_key,
                self.target_change_id,
                self.user_id,
                self.usage_ids,
                self.learning_package_id,
                self.composition_level,
                self.override
            )

        mock_validate_composition_level.side_effect = None
        mock_validate_usage_keys.side_effect = ValueError("Invalid usage keys")

        with self.assertRaises(ValueError):
            import_course_to_library(
                self.source_key,
                self.target_change_id,
                self.user_id,
                self.usage_ids,
                self.learning_package_id,
                self.composition_level,
                self.override
            )
