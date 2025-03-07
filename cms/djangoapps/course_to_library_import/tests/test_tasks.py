"""
Tests for tasks in course_to_library_import app.
"""

from unittest.mock import patch

from django.test import TestCase
from opaque_keys.edx.keys import CourseKey

from cms.djangoapps.course_to_library_import.tasks import save_course_to_staged_content_task


class TestSaveCourseSectionsToStagedContentTask(TestCase):
    """
    Test cases for save_course_sections_to_staged_content_task.
    """

    @patch('cms.djangoapps.course_to_library_import.tasks.modulestore')
    @patch('openedx.core.djangoapps.content_staging.api.stage_xblock_temporarily')
    def test_save_course_sections_to_staged_content_task(self, mock_stage_xblock_temporarily, mock_modulestore):

        course_id = 'course-v1:edX+DemoX+Demo_Course'
        user_id = 1
        purpose = 'test_purpose'
        version_num = 1

        mock_course_key = CourseKey.from_string(course_id)
        mock_modulestore().get_items.return_value = sections = ['section1', 'section2']

        save_course_to_staged_content_task(course_id, user_id, purpose, version_num)

        mock_modulestore().get_items.assert_called_once_with(mock_course_key, qualifiers={'category': 'chapter'})

        self.assertEqual(mock_stage_xblock_temporarily.call_count, len(sections))
        for section in sections:
            mock_stage_xblock_temporarily.assert_any_call(section, user_id, purpose=purpose, version_num=version_num)
