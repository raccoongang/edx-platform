"""
Tests for edx_global_analytics application helper functions aka utils.
"""

import datetime

from django.test import TestCase
from django.utils import timezone

from django.db.models import Q
from django_countries.fields import Country

from student.models import UserProfile
from student.tests.factories import UserFactory

from ..utils import fetch_instance_information, cache_instance_data


class TestStudentsAmountPerParticularPeriod(TestCase):
    """
    Tests cover all methods, that have a deal with statistics calculation.
    """
    @staticmethod
    def active_students_amount_default_data():
        """
        Default integration and particular data for active students amount functionality.
        """
        users_last_login = [
            timezone.make_aware(datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 00, 00, 00), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 00, 00, 00), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 00, 00, 01), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

        return activity_period, cache_timeout

    def test_expected_result_fetch_instance_information_for_active_students_amount(self):
        """
        Verifies that fetch_instance_information returns data as expected in particular period and accurate datetime.
        We have no reason to test week and month periods for active students amount,
        all queries are the same, we just go test only day period.
        """
        activity_period, cache_timeout = self.active_students_amount_default_data()

        result = fetch_instance_information(
            'active_students_amount_day', 'active_students_amount', activity_period, cache_timeout
        )

        self.assertEqual(result, 2)

    def test_miss_statistics_query_fetch_instance_information_for_active_students_amount(self):
        """
        Verifies that fetch_instance_information raise `KeyError` if default statistics queries don't have
        corresponding name (dict`s key).
        """
        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

        self.assertRaises(KeyError, lambda: fetch_instance_information(
            'active_students_amount_day', 'active_students_amount_day', activity_period, cache_timeout
        ))

    def test_datetime_is_none_fetch_instance_information_for_active_students_amount(self):
        """
        Verifies that fetch_instance_information raise `TypeError` if needed datetime objects are missed
        as activity period is None.
        """
        activity_period, cache_timeout = None, None

        self.assertRaises(TypeError, lambda: fetch_instance_information(
            'active_students_amount_day', 'active_students_amount', activity_period, cache_timeout
        ))

    def test_fetch_instance_information_for_students_per_country(self):
        """
        Verifies that students_per_country returns data as expected in particular period and accurate datetime.
        """
        last_login = timezone.make_aware(datetime.datetime(2017, 5, 15, 14, 23, 23), timezone.get_default_timezone())
        countries = [u'US', u'CA']

        for country in countries:
            self.user = UserFactory.create(last_login=last_login)
            self.profile = self.user.profile
            self.profile.country = Country(country)
            self.profile.save()

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

        result = fetch_instance_information(
            'students_per_country', 'students_per_country', activity_period, cache_timeout)

        self.assertItemsEqual(result, {u'US': 1, u'CA': 1})

    def test_no_students_with_country_fetch_instance_information_for_students_per_country(self):
        """
        Verifies that students_per_country returns data as expected if no students with country.
        """
        last_login = timezone.make_aware(datetime.datetime(2017, 5, 15, 14, 23, 23), timezone.get_default_timezone())

        for country in range(2):
            self.user = UserFactory.create(last_login=last_login)

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

        result = fetch_instance_information(
            'students_per_country', 'students_per_country', activity_period, cache_timeout)

        self.assertEqual(result, {None: 0})


class TestCacheInstanceData(TestCase):
    """
    Tests cover cache-functionality for queries results.
    """
    @staticmethod
    def cache_instance_data_default_data():
        """
        Default integration and particular data for cache instance information tests.
        """
        users_last_login = [
            timezone.make_aware(datetime.datetime(2017, 5, 8, 00, 00, 00), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 00, 00, 00), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 00, 00, 01), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

        period_start, period_end = datetime.date(2017, 5, 8), datetime.date(2017, 5, 15)

        return period_start, period_end

    def test_cache_instance_data(self):
        """
        Verifies that cache_instance_dat returns data as expected after caching it.
        """
        period_start, period_end = self.cache_instance_data_default_data()

        active_students_amount_week = UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

        cache_timeout = None

        result = cache_instance_data('active_students_amount_week', active_students_amount_week, cache_timeout)

        self.assertEqual(result, 2)
