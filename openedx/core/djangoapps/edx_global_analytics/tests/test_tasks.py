"""
Tests for edx_global_analytics application tasks and helper functions.
"""

from django.test import TestCase

from ..tasks import platform_coordinates


class TestInstallationInformation(TestCase):
    """
    Tests cover all methods, that have a deal with overall edX instance information.
    """
    def test_expected_result_for_platform_coordinates(self):
        """
        Verifies that platform_coordinates returns city latitude and longitude as expected.
        """
        result = platform_coordinates('Kiev')

        self.assertEqual(result, (50.4501, 30.5234))

    def test_miss_city_in_settings_for_platform_coordinates(self):
        """
        Verifies that platform_coordinates returns city latitude and longitude although city name in settings is empty.
        Functions gather latitude and longitude by ip with FreeGeoIP service.

        Function can't check all cases. We accept as right if it returns float variables, that aren't None.
        """
        for coordinate in platform_coordinates(''):
            self.assertIsInstance(coordinate, float)
            self.assertIsNotNone(coordinate)

    def test_wrong_city_name_in_settings_for_platform_coordinates(self):
        """
        Verifies that platform_coordinates returns city latitude and longitude although city name in settings is wrong.
        Functions gather latitude and longitude by ip with FreeGeoIP service.

        Function can't check all cases. We accept as right if it returns float variables, that aren't None.
        """
        for coordinate in platform_coordinates('Lmnasasfabqwrqrn'):
            self.assertIsInstance(coordinate, float)
            self.assertIsNotNone(coordinate)
