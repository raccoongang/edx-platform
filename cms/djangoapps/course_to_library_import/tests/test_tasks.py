"""
Tests for tasks in course_to_library_import app.
"""

from unittest.mock import patch

from django.test import TestCase
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import LibraryLocatorV2

from cms.djangoapps.course_to_library_import.data import CourseToLibraryImportStatus
from cms.djangoapps.course_to_library_import.tasks import (
    import_library_from_staged_content_task,
    save_courses_to_staged_content_task,
)
from common.djangoapps.student.tests.factories import UserFactory

from .factories import CourseToLibraryImportFactory


class TestSaveCourseSectionsToStagedContentTask(TestCase):
    """
    Test cases for save_course_sections_to_staged_content_task.
    """

    @patch('cms.djangoapps.course_to_library_import.tasks.modulestore')
    @patch('openedx.core.djangoapps.content_staging.api.stage_xblock_temporarily')
    def test_save_courses_to_staged_content_task(self, mock_stage_xblock_temporarily, mock_modulestore):
        course_to_library_import = CourseToLibraryImportFactory()
        course_ids = course_to_library_import.course_ids.split(' ')
        user_id = course_to_library_import.user.id
        purpose = 'test_purpose'
        version_num = 1

        mock_course_keys = [CourseKey.from_string(course_id) for course_id in course_ids]
        mock_modulestore().get_items.return_value = sections = ['section1', 'section2']

        self.assertEqual(course_to_library_import.status, CourseToLibraryImportStatus.PENDING)

        save_courses_to_staged_content_task(course_ids, user_id, course_to_library_import.id, purpose, version_num)

        for mock_course_key in mock_course_keys:
            mock_modulestore().get_items.assert_any_call(mock_course_key, qualifiers={"category": "chapter"})

        self.assertEqual(mock_stage_xblock_temporarily.call_count, len(sections) * len(course_ids))
        for section in sections:
            mock_stage_xblock_temporarily.assert_any_call(section, user_id, purpose=purpose, version_num=version_num)


class TestImportLibraryFromStagedContentTask(TestCase):
    """
    Test cases for import_library_from_staged_content_task.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.user = UserFactory()
        self.usage_ids = ["block-v1:org+course+run+type@sequential+block@1234"]
        self.library_key = "lib:org:test-lib"
        self.purpose = "test_purpose"
        self.override = False

    @patch('cms.djangoapps.course_to_library_import.tasks.CourseToLibraryImport.objects.filter')
    @patch('cms.djangoapps.course_to_library_import.tasks.validate_usage_ids')
    @patch('cms.djangoapps.course_to_library_import.tasks.flat_import_children')
    @patch('cms.djangoapps.course_to_library_import.tasks.get_block_to_import')
    @patch('cms.djangoapps.course_to_library_import.tasks.content_staging_api')
    @patch('cms.djangoapps.course_to_library_import.tasks.etree')
    def test_import_library_from_staged_content_task_success(
        self, mock_etree, mock_content_staging_api, mock_get_block_to_import,
        mock_flat_import_children, mock_validate_usage_ids, mock_filter
    ):
        """
        Test successful execution of import_library_from_staged_content_task.
        """
        # Setup mocks
        mock_staged_content = mock_content_staging_api.get_ready_staged_content_by_user_and_purpose.return_value
        mock_staged_content_item = mock_staged_content.filter.return_value.first.return_value
        mock_staged_content_item.olx = "<olx>content</olx>"
        mock_get_block_to_import.return_value = "block_data"

        # Execute the task
        import_library_from_staged_content_task(
            self.user.id, self.usage_ids, self.library_key, self.purpose, self.override
        )

        # Verify the functions were called with correct parameters
        mock_content_staging_api.get_ready_staged_content_by_user_and_purpose.assert_called_once_with(
            self.user.id, self.purpose
        )
        mock_validate_usage_ids.assert_called_once_with(self.usage_ids, mock_staged_content)
        mock_staged_content.filter.assert_called_once_with(tags__icontains=self.usage_ids[0])
        mock_etree.fromstring.assert_called_once_with(mock_staged_content_item.olx, parser=mock_etree.XMLParser())
        mock_get_block_to_import.assert_called_once()
        mock_flat_import_children.assert_called_once()

        # Verify the CourseToLibraryImport status was updated
        mock_filter.assert_called_with(
            user_id=self.user.id, library_key=LibraryLocatorV2.from_string(self.library_key)
        )
        mock_staged_content.delete.assert_called_once()
