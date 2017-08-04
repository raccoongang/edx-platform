"""
Tests for edX global analytics application cache functionality.
"""

from datetime import date

from mock import patch
from django.test import TestCase

from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import (
    cache_instance_data,
    get_cache_week_key,
    get_cache_month_key,
)


@patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.cache')
class TestCacheInstanceData(TestCase):
    """
    Tests for cache instance data method.
    """

    def test_cache_query_does_not_exists(self, mock_cache):
        """
        Verify that cache_instance_data method return cached query result if it exists in cache.
        """
        mock_cache.get.return_value = True
        cache_instance_data('name_to_cache', 'query_type', 'activity_period')

        mock_cache.set.assert_not_called()

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.get_query_result')
    def test_cache_query_exists(self, mock_get_query_result, mock_cache):
        """
        Verify that cache_instance_data method set query result if it does not exists in cache.
        """
        mock_cache.get.return_value = None
        mock_get_query_result.return_value = 'query_result'

        cache_instance_data('name_to_cache', 'active_students_amount', 'activity_period')

        mock_cache.set.assert_called_once_with('name_to_cache', 'query_result')


@patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.date')
class TestCacheInstanceDataHelpFunctions(TestCase):
    """
    Tests for cache help functions.
    """

    def test_cache_timeout_week(self, mock_date):
        """
        Verify that get_cache_week_key returns correct cache key.

        9 January is a monday, it is second week from year's start.
        get_cache_week_key returns previous week `year` and `week` numbers.
        """
        mock_date.today.return_value = date(2017, 1, 9)

        result = get_cache_week_key()

        self.assertEqual('2017-1-week', result)

    def test_cache_timeout_month(self, mock_date):
        """
        Verify that get_cache_month_key returns correct cache key.

        4th month is an April.
        get_cache_month_key returns previous month `year` and `month` numbers.
        """
        mock_date.today.return_value = date(2017, 4, 9)

        result = get_cache_month_key()

        self.assertEqual('2017-3-month', result)
