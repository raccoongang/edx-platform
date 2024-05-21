import unittest
from unittest.mock import patch, Mock
from django.test import TestCase
from django.dispatch import Signal

from lms.djangoapps.offline_mode.handlers import listen_course_publish
from lms.djangoapps.offline_mode.tasks import generate_course_media

# Mocking the XBLOCK_PUBLISHED signal
XBLOCK_PUBLISHED = Signal(providing_args=["course_key"])

class ListenCoursePublishSignalTest(TestCase):

    def setUp(self):
        self.course_key = 'course-v1:edX+DemoX+Demo_Course'

    @patch('myapp.signals.generate_course_media.delay')
    @patch('myapp.signals.USER_TOURS_DISABLED.is_disabled', return_value=False)
    def test_listen_course_publish_signal_handler(self, mock_is_disabled, mock_generate_course_media):
        # Simulate sending the signal
        XBLOCK_PUBLISHED.send(sender=None, course_key=self.course_key)

        # Check if the generate_course_media task was called with the correct arguments
        mock_generate_course_media.assert_called_once_with(self.course_key)

    @patch('myapp.signals.generate_course_media.delay')
    @patch('myapp.signals.USER_TOURS_DISABLED.is_disabled', return_value=True)
    def test_listen_course_publish_signal_handler_disabled(self, mock_is_disabled, mock_generate_course_media):
        # Simulate sending the signal
        XBLOCK_PUBLISHED.send(sender=None, course_key=self.course_key)

        # Check that the generate_course_media task was not called since the feature is disabled
        mock_generate_course_media.assert_not_called()
