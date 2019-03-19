"""
Tests for edX global analytics application functions, that help to calculate statistics.
"""

from datetime import date

from ddt import ddt, data, unpack
from mock import patch
from django.test import TestCase

from openedx.core.djangoapps.edx_global_analytics.utils.utilities import (
    get_previous_day_start_and_end_dates,
    get_previous_week_start_and_end_dates,
    get_previous_month_start_and_end_dates,
)


@ddt
@patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.date')
class TestStudentsAmountPerParticularPeriodHelpFunctions(TestCase):
    """
    Tests for edX global analytics application functions, that help to calculate statistics.
    """

    @data(
        [get_previous_day_start_and_end_dates, (date(2017, 6, 13), date(2017, 6, 14))],
        [get_previous_week_start_and_end_dates, (date(2017, 6, 5), date(2017, 6, 12))],
        [get_previous_month_start_and_end_dates, (date(2017, 5, 1), date(2017, 6, 1))],
    )
    @unpack
    def test_calendar_periods(self, calendar_period, expected_result, mock_date):
        """
        Verify that methods, that gather calendar period return expected day start and end dates.

        Test to prove:
            - that get_previous_day_start_and_end_dates returns expected previous day start and end dates.
            - that test_get_previous_week_start_and_end_dates returns expected previous week start and end dates.
            - that test_get_previous_month_start_and_end_dates returns expected previous month start and end dates.
        """

        mock_date.today.return_value = date(2017, 6, 14)

        self.assertEqual(expected_result, calendar_period())
