"""
Tests for statistics level bunches, that provides particular edX installation statistics.
"""

import unittest
from datetime import date

from mock import patch

from openedx.core.djangoapps.edx_global_analytics.utils.utilities import get_previous_day_start_and_end_dates
from openedx.core.djangoapps.edx_global_analytics.tasks import (
    enthusiast_level_statistics_bunch,
    paranoid_level_statistics_bunch
)


@patch('openedx.core.djangoapps.edx_global_analytics.tasks.fetch_instance_information')
class TestStatisticsLevelBunches(unittest.TestCase):
    """
    Tests for statistics level bunches, that provides particular edX installation statistics.
    """

    def test_paranoid_statistics_result(self, mock_fetch_instance_information):
        """
        Verify that paranoid_level_statistics_bunch_method returns active students amount per day, week and month.
        """
        mock_fetch_instance_information.return_value = 5

        result = paranoid_level_statistics_bunch()

        self.assertEqual(
            (5, 5, 5), result
        )

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.get_previous_day_start_and_end_dates')
    def test_fetching_enthusiast_statistics(
            self, mock_get_previous_day_start_and_end_dates, mock_fetch_instance_information
    ):
        """
        Verify that enthusiast_level_statistics_bunch_method calls needed fetch instance information method for
        students per country.
        """
        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 7, 3), date(2017, 7, 4)

        enthusiast_level_statistics_bunch()

        mock_fetch_instance_information.assert_called_once_with(
            'students_per_country', get_previous_day_start_and_end_dates(), name_to_cache=None
        )

    def test_enthusiast_statistics_result(self, mock_fetch_instance_information):
        """
        Verify that enthusiast_level_statistics_bunch_method return students per country statistics.
        """
        mock_students_per_country = {'US': 5, 'CA': 10}
        mock_fetch_instance_information.return_value = mock_students_per_country

        result = enthusiast_level_statistics_bunch()

        self.assertEqual(mock_students_per_country, result)
