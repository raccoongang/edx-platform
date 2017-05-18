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

    def test_fetch_instance_information_for_active_students_amount(self):
        """
        Verifies that fetch_instance_information returns data as expected in particular period and accurate datetime.
        We have no reason to test week and month periods for active students amount,
        all queries are the same, we just go test only day period.
        """
        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 15, 00, 00, 00), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 15, 23, 59, 59), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 16, 00, 00, 00), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 16, 00, 00, 01), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 16, 00, 00, 01), timezone.get_default_timezone()),
        )

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        cache_timeout = None

        result = fetch_instance_information(
            'active_students_amount_day', 'active_students_amount', activity_period, cache_timeout)

        self.assertEqual(result, 2)

    def test_fetch_instance_information_for_students_per_country(self):
        """
        Verifies that students_per_country returns data as expected in particular period and accurate datetime.
        """
        last_login = timezone.make_aware(datetime.datetime(2017, 5, 15, 14, 23, 23), timezone.get_default_timezone())

        self.user_first = UserFactory.create(last_login=last_login)
        self.profile = self.user_first.profile
        self.profile.country = Country(u'US')
        self.profile.save()

        self.user_second = UserFactory.create(last_login=last_login)
        self.profile = self.user_second.profile
        self.profile.country = Country(u'CA')
        self.profile.save()

        activity_period = datetime.date(2017, 5, 10), datetime.date(2017, 5, 20)
        cache_timeout = None

        result = fetch_instance_information(
            'students_per_country', 'students_per_country', activity_period, cache_timeout)

        self.assertItemsEqual(result, {u'US': 1, u'CA': 1})


class TestCacheInstanceData(TestCase):
    """
    Tests cover cache-functionality for queries results.
    """
    def test_cache_instance_data(self):
        """
        Verifies that cache_instance_dat returns data as expected after caching it.
        """
        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 8, 00, 00, 00), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone())
        )

        UserFactory(last_login=timezone.make_aware(
            datetime.datetime(2017, 5, 15, 00, 00, 01), timezone.get_default_timezone())
        )

        period_start, period_end = datetime.date(2017, 5, 8), datetime.date(2017, 5, 15)

        active_students_amount_week = UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

        cache_timeout = None

        result = cache_instance_data('active_students_amount_week', active_students_amount_week, cache_timeout)

        self.assertEqual(result, 2)
