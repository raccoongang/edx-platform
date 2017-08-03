"""
Tests for edX global analytics application cache functionality.
"""

from datetime import date, datetime

from mock import patch

from django.test import TestCase
from django.utils import timezone
from django.db.models import Q

from student.models import UserProfile
from student.tests.factories import UserFactory

from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import (
    cache_instance_data,
    cache_timeout_month,
    cache_timeout_week,
)


class TestCacheInstanceData(TestCase):
    """
    Test cover cache-functionality for queries results.
    """


    @staticmethod
    def create_default_data():
        """
        Default integration database data for cache instance information tests.
        """
        users_last_login = [
            timezone.make_aware(datetime(2017, 5, 8, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime(2017, 5, 15, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime(2017, 5, 15, 0, 0, 1), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

    def test_cache_new_instance_data(self):
        """
        Verify that cache_instance_data returns data as expected after caching it.
        """
        self.create_default_data()

        period_start, period_end = date(2017, 5, 8), date(2017, 5, 15)

        active_students_amount_week = UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

        cache_timeout = None

        result = cache_instance_data('active_students_amount_week', active_students_amount_week, cache_timeout)

        self.assertEqual(result, 2)

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.cache.get')
    @patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.cache.set')
    def test_returning_existed_query_result(self, mock_cache_set, mock_cache_get):
        """
        Verify that cache_instance_data returns data as expected if it already exists in cache.
        """
        mock_cache_get.return_value = 'mock_cached_query_result'

        cache_instance_data('None', None, None)

        self.assertEqual(0, mock_cache_set.call_count)


@patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.datetime')
class TestCacheInstanceDataHelpFunctions(TestCase):
    """
    Tests for cache help functions.
    """

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.cache_utils.date')
    def test_cache_timeout_week(self, mock_date, mock_datetime):
        """
        Verify cache_timeout_week returns correct cache timeout seconds.
        """
        mock_datetime.now.return_value = datetime(2017, 7, 9, 23, 55, 0)
        mock_date.today.return_value = date(2017, 7, 9)

        result = cache_timeout_week()

        self.assertEqual(299, result)

    def test_cache_timeout_month(self, mock_datetime):
        """
        Verify cache_timeout_week returns correct cache timeout seconds.
        """
        mock_datetime.now.return_value = datetime(2017, 7, 31, 21, 59, 59)

        result = cache_timeout_month()

        self.assertEqual(7200, result)
