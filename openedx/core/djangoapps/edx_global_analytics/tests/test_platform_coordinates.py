"""
Tests for edx global analytics application tasks and helper functions.
"""

import unittest

import requests
from mock import patch, call

from openedx.core.djangoapps.edx_global_analytics.utils.utilities import get_coordinates_by_ip


@patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.requests.get')
class TestPlatformCoordinates(unittest.TestCase):
    """
    Tests for platform coordinates methods, that gather latitude and longitude.
    """

    def tests_sending_requests(self, mock_request):
        """
        Tests to prove that methods send request to needed corresponding URLs.
        """

        # Verify that get_coordinates_by_ip sends request to FreeGeoIP API.
        get_coordinates_by_ip()

        expected_calls = [
            call('https://freegeoip.net/json'),
        ]

        self.assertEqual(mock_request.call_args_list, expected_calls)

    def test_get_coordinates_by_ip_result(self, mock_request):
        """
        Verify that get_coordinates_by_ip returns city latitude and longitude as expected.
        """
        mock_request.return_value.json.return_value = {
            'lat': 49.9942,
            'lon': 36.2339
        }

        latitude, longitude = get_coordinates_by_ip()
        self.assertEqual(
            (49.9942, 36.2339), (latitude, longitude)
        )

    def test_get_coordinates_by_ip_if_exception(self, mock_request):
        """
        Verify that get_coordinates_by_ip returns empty latitude and longitude after request exception.
        """
        mock_request.side_effect = requests.RequestException()
        latitude, longitude = get_coordinates_by_ip()
        self.assertEqual(
            ('', ''), (latitude, longitude)
        )
