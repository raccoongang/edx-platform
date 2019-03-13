"""
Tests for edx global analytics application tasks and helper functions.
"""

import unittest

from mock import call, patch

from openedx.core.djangoapps.edx_global_analytics.utils.utilities import get_coordinates_by_ip


@patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.requests.get')
class TestPlatformCoordinates(unittest.TestCase):
    """
    Tests for platform coordinates method, that gather latitude and longitude.
    """

    def tests_sending_requests(self, mock_request):
        """
        Test to prove that method sends request to needed corresponding URL.
        """

        # Verify that get_coordinates_by_ip sends request to FreeGeoIP API.
        get_coordinates_by_ip()

        expected_calls = [
            call('http://ip-api.com/json'),
        ]

        self.assertEqual(mock_request.call_args_list, expected_calls)

    def test_get_coordinates_by_ip_if_exception(self, mock_request):
        """
        Verify that get_coordinates_by_ip returns empty latitude and longitude after request exception.
        """
        mock_request.return_value.ok = False

        latitude, longitude = get_coordinates_by_ip()
        self.assertEqual(('', ''), (latitude, longitude))
