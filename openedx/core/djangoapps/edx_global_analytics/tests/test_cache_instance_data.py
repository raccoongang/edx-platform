"""
Tests for edX global analytics application cache functionality.
"""

from datetime import date

from ddt import ddt, data, unpack
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

        cache_instance_data('name_to_cache', 'query_type', 'activity_period')

        mock_cache.set.assert_called_once_with('name_to_cache', 'query_result')


@ddt
class TestCacheInstanceDataHelpFunctions(TestCase):
    """
    Tests for cache help functions.
    """

    @data(
        [date(2017, 1, 9), get_cache_week_key, '2017-1-week'],
        [date(2017, 4, 9), get_cache_month_key, '2017-3-month']
    )
    @unpack
    @patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.date')
    def test_cache_keys(self, fake_date, get_cache_key, expected_result, mock_date):
        """
        Verify that `get cache key` methods return correct cache keys.

        `get_cache_week_key`:
            - 9th January is a monday, it is second week from year's start.
            - returns previous week `year` and `week` numbers.

        `get_cache_month_key`:
            - 4th month is an April.
            - get_cache_month_key returns previous month `year` and `month` numbers.
        """
        mock_date.today.return_value = fake_date

        result = get_cache_key()

        self.assertEqual(expected_result, result)
