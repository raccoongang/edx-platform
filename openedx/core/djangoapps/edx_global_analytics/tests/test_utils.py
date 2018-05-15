"""
Tests for edx_global_analytics application helper functions aka utils.
"""

import datetime
import logging
import pytest

from certificates.models import GeneratedCertificate
from django.test import TestCase
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django_countries.fields import Country

from student.models import UserProfile
from student.tests.factories import UserFactory
from openedx.core.djangoapps.edx_global_analytics.utils.utilities import (
    fetch_instance_information,
    cache_instance_data,
    get_registered_students_daily,
    get_generated_certificates_daily,
    get_last_analytics_sent_date,
    get_enthusiastic_students_daily,
)
from openedx.core.djangoapps.edx_global_analytics.tasks import set_last_sent_date


class TestStudentsAmountPerParticularPeriod(TestCase):
    """
    Tests cover all methods, that have a deal with statistics calculation.
    """
    @staticmethod
    def create_active_students_amount_default_database_data():
        """
        Default integration database data for active students amount functionality.
        """
        users_last_login = [
            timezone.make_aware(datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 0, 0, 1), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

    def test_expected_result_fetch_instance_information_for_active_students_amount(self):
        """
        Verifies that fetch_instance_information returns data as expected in particular period and accurate datetime.
        We have no reason to test week and month periods for active students amount,
        all queries are the same, we just go test only day period.
        """
        self.create_active_students_amount_default_database_data()

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

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
            user = UserFactory.create(last_login=last_login)
            profile = user.profile
            profile.country = Country(country)
            profile.save()

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

        UserFactory.create(last_login=last_login)

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
    def create_cache_instance_data_default_database_data():
        """
        Default integration database data for cache instance information tests.
        """
        users_last_login = [
            timezone.make_aware(datetime.datetime(2017, 5, 8, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 0, 0, 1), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

    def test_cache_instance_data(self):
        """
        Verifies that cache_instance_data returns data as expected after caching it.
        """
        self.create_cache_instance_data_default_database_data()

        period_start, period_end = datetime.date(2017, 5, 8), datetime.date(2017, 5, 15)

        active_students_amount_week = UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

        cache_timeout = None

        result = cache_instance_data('active_students_amount_week', active_students_amount_week, cache_timeout)

        self.assertEqual(result, 2)


class TestLastSentStatisticsDate(TestCase):
    """
    Tests the dates of the last sent statistics.
    """

    def test_cache_returns_default_and_latest_dates(self):
        """
        Verifies that cache returns the default stats date (the Unix epoch start).
        """
        cache.clear()
        data = {
            'registered_students': {
                '2017-01-01': 17,
                '2018-01-01': 18,
            },
            'generated_certificates': {
                '2016-01-01': 16,
            },
            'enthusiastic_students': {
            },
        }
        token = 'test-token'
        default_date1 = get_last_analytics_sent_date('registered_students', token)
        default_date2 = get_last_analytics_sent_date('enthusiastic_students', token)

        set_last_sent_date(True, token, data)

        registered_students = get_last_analytics_sent_date('registered_students', token)
        certs_latest = get_last_analytics_sent_date('generated_certificates', token)

        default_date = datetime.datetime.fromtimestamp(0)
        self.assertEqual(default_date1, default_date)
        self.assertEqual(default_date2, default_date)

        self.assertEqual(registered_students, datetime.datetime.strptime('2018-01-01', '%Y-%m-%d'))
        self.assertEqual(certs_latest, datetime.datetime.strptime('2016-01-01', '%Y-%m-%d'))


class TestGetStatsDailyRegistered(TestCase):
    """
    Tests the data returned about the registered users.
    """

    def test_return_non_data_on_newest_date(self):
        """
        Checks that the function returns an empty dict by the date in filter that didn't existed yet.
        """
        self.assertEqual(len(get_registered_students_daily('test-token')), 0)

    def test_return_data_on_previous_dates(self):
        """
        Checks that the function returns a  dict by the past date in filter.
        """
        cache.clear()
        User.objects.create(username='test1', password='test1', email='test1@example.com', date_joined='2016-01-01')
        User.objects.create(username='test2', password='test2', email='test2@example.com', date_joined='2016-01-01')
        User.objects.create(username='test3', password='test3', email='test3@example.com', date_joined='2017-01-01')
        first_students_part = get_registered_students_daily('test-token')

        self.assertEqual(len(first_students_part), 2)
        self.assertEqual(first_students_part['2016-01-01'], 2)
        self.assertEqual(first_students_part['2017-01-01'], 1)

        data = {
            'registered_students': {
                '2016-01-01': 2,
                '2017-01-01': 1,
            },
            'generated_certificates': {},
            'enthusiastic_students': {},
        }
        set_last_sent_date(True, 'test-token', data)  # Saving the last date

        User.objects.create(username='test4', password='test4', email='test4@example.com', date_joined='2018-01-01')
        second_students_part = get_registered_students_daily('test-token')

        self.assertEqual(len(second_students_part), 1)
        self.assertEqual(second_students_part['2018-01-01'], 1)


class TestGetStatsDailyCertificates(TestCase):
    """
    Tests the data returned about the generated certificates.
    """

    def test_return_non_data_on_newest_date(self):
        """
        Checks that the function returns an empty dict by the date in filter that didn't existed yet.
        """
        self.assertEqual(len(get_generated_certificates_daily('test-token')), 0)

    def test_return_data_on_previous_dates(self):
        """
        Checks that the function returns a  dict by the past date in filter.
        """
        cache.clear()
        User.objects.create(username='test1', password='test1', email='test1@example.com', date_joined='2016-01-01')
        User.objects.create(username='test2', password='test2', email='test2@example.com', date_joined='2016-01-01')
        User.objects.create(username='test3', password='test3', email='test3@example.com', date_joined='2017-01-01')
        GeneratedCertificate.objects.create(user_id=1, created_date='2016-01-01')
        GeneratedCertificate.objects.create(user_id=2, created_date='2016-01-01')
        GeneratedCertificate.objects.create(user_id=3, created_date='2017-01-01')
        first_certificates_part = get_generated_certificates_daily('test-token')

        self.assertEqual(len(first_certificates_part), 2)
        self.assertEqual(first_certificates_part['2016-01-01'], 2)
        self.assertEqual(first_certificates_part['2017-01-01'], 1)

        data = {
            'registered_students': {},
            'generated_certificates': {
                '2016-01-01': 2,
                '2017-01-01': 1,
            },
            'enthusiastic_students': {},
        }
        set_last_sent_date(True, 'test-token', data)  # Saving the last date

        User.objects.create(username='test4', password='test4', email='test4@example.com', date_joined='2018-01-01')
        GeneratedCertificate.objects.create(user_id=4, created_date='2018-01-01')
        second_certificates_part = get_generated_certificates_daily('test-token')

        self.assertEqual(len(second_certificates_part), 1)
        self.assertEqual(second_certificates_part['2018-01-01'], 1)


class TestGetStatsDailyEnthusiastic(TestCase):
    """
    Tests the data returned about the generated certificates.
    """

    def test_return_non_data_on_newest_date(self):
        """
        Checks that the function returns an empty dict by the date in filter that didn't existed yet.
        """
        self.assertEqual(len(get_enthusiastic_students_daily('test-token')), 0)
