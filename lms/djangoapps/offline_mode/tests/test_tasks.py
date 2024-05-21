# lint-amnesty, pylint: disable=missing-module-docstring
from unittest import mock
from unittest.mock import patch

import ddt
from django.test import TestCase
from celery import shared_task

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase  # lint-amnesty, pylint: disable=wrong-import-order
from opaque_keys.edx.keys import CourseKey

from lms.djangoapps.offline_mode.tasks import generate_course_media
from lms.djangoapps.offline_mode.utils.xblock_helpers import (
    generate_offline_content,
    xblock_view_handler,
    generate_request_with_service_user,
    is_offline_supported,
)


@ddt.ddt
class TestGenerateCourseMediaTask(ModuleStoreTestCase):  # lint-amnesty, pylint: disable=missing-class-docstring
    @patch('lms.djangoapps.offline_mode.tasks.generate_request_with_service_user')
    @patch('lms.djangoapps.offline_mode.tasks.modulestore')
    @patch('lms.djangoapps.offline_mode.tasks.xblock_view_handler')
    @patch('lms.djangoapps.offline_mode.tasks.generate_offline_content')
    @patch('lms.djangoapps.offline_mode.tasks.is_offline_supported')
    def test_generate_course_media(self, mock_is_offline_supported, mock_generate_offline_content, mock_xblock_view_handler, mock_modulestore, mock_generate_request_with_service_user):
        # Arrange
        course_id = 'course-v1:edX+DemoX+Demo_Course'
        course_key = CourseKey.from_string(course_id)
        request = mock.Mock()
        mock_generate_request_with_service_user.return_value = request
        mock_xblock = mock.Mock(category='problem')
        mock_modulestore().get_items.return_value = [mock_xblock]
        mock_is_offline_supported.return_value = False
        html_data = '<div>Sample HTML</div>'
        mock_xblock_view_handler.return_value = html_data

        # Act
        generate_course_media(course_id)

        # Assert
        mock_generate_request_with_service_user.assert_called_once()
        mock_modulestore().get_items.assert_called_once_with(course_key, qualifiers={'category': 'problem'})
        mock_is_offline_supported.assert_called_once_with(mock_xblock)
        mock_xblock_view_handler.assert_called_once_with(request, mock_xblock)
        mock_generate_offline_content.assert_called_once_with(mock_xblock, html_data)

    @patch('lms.djangoapps.offline_mode.tasks.generate_request_with_service_user')
    @patch('lms.djangoapps.offline_mode.tasks.modulestore')
    @patch('lms.djangoapps.offline_mode.tasks.is_offline_supported')
    def test_generate_course_media_offline_supported(self, mock_is_offline_supported, mock_modulestore, mock_generate_request_with_service_user):
        # Arrange
        course_id = 'course-v1:edX+DemoX+Demo_Course'
        course_key = CourseKey.from_string(course_id)
        request = mock.Mock()
        mock_generate_request_with_service_user.return_value = request
        mock_xblock = mock.Mock(category='problem')
        mock_modulestore().get_items.return_value = [mock_xblock]
        mock_is_offline_supported.return_value = True

        # Act
        generate_course_media(course_id)

        # Assert
        mock_generate_request_with_service_user.assert_called_once()
        mock_modulestore().get_items.assert_called_once_with(course_key, qualifiers={'category': 'problem'})
        mock_is_offline_supported.assert_called_once_with(mock_xblock)
        self.assertFalse(mock_xblock_view_handler.called)
        self.assertFalse(mock_generate_offline_content.called)
