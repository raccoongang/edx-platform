"""
Helpers for the edX global analytics application.
"""

import datetime
import calendar

from django.core.cache import cache

from django.db.models import Count
from django.db.models import Q
from student.models import UserProfile


def calculate_active_students_amount(query_name, activity_period):
    """
    Calculates instance active students amount for particular period as like as previous calendar day,
    week and month after cached.
    """
    period_start, period_end = activity_period

    active_students_amount = UserProfile.objects.exclude(
        Q(user__last_login=None) | Q(user__is_active=False)
    ).filter(user__last_login__gt=period_start, user__last_login__lt=period_end).count()

    if query_name is not 'active_students_amount_day':
        clear_cache_date = period_end
        return caching_instance_data(query_name, active_students_amount, clear_cache_date)

    return active_students_amount


def calculate_students_per_country(query_name, activity_period):
    """
    Calculates instance students per country amount for particular period as like as previous calendar day,
    week and month after cached.

    Returns:
        students_per_country_after_cached (dict): Country-count accordance as pair of key-value.
                                                  Example: {u'FR': 3434, u'UA': 1124}
    """
    period_start, period_end = activity_period

    students_per_country = dict(UserProfile.objects.exclude(
        Q(user__last_login=None) | Q(user__is_active=False)
    ).filter(user__last_login__gt=period_start, user__last_login__lt=period_end
    ).values('country').annotate(count=Count('country')).values_list('country', 'count'))

    clear_cache_date = period_end
    students_per_country_after_cached = caching_instance_data(query_name, students_per_country, clear_cache_date)

    return students_per_country_after_cached


def get_previous_day_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar day.

    Returns:
        start_of_day (date): Previous day`s start. Example for 2017-05-15 is 2017-05-15.
        end_of_day (date): Previous day`s end, it`s a next day (tomorrow) toward day`s start,
                           that doesn't count in segment. Example for 2017-05-15 is 2017-05-16.
    """
    end_of_day = datetime.date.today()
    start_of_day = end_of_day - datetime.timedelta(days=1)

    return start_of_day, end_of_day


def get_previous_week_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar week.

    Returns:
        start_of_month (date): Calendar week`s start day. Example for may is 2017-05-08.
        end_of_month (date): Calendar week`s end day, it`s the first day of next week, that doesn't count in segment.
                             Example for may is 2017-05-15.
    """
    days_after_week_started = datetime.date.today().weekday() + 7

    start_of_week = datetime.date.today() - datetime.timedelta(days=days_after_week_started)
    end_of_week = start_of_week + datetime.timedelta(days=7)

    return start_of_week, end_of_week


def get_previous_month_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar month.

    Returns:
        start_of_month (date): Calendar month`s start day. Example for may is 2017-04-01.
        end_of_month (date): Calendar month`s end day, it`s the first day of next month, that doesn't count in segment.
                             Example for may is 2017-05-01.
    """
    previous_month_date = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)

    start_of_month = previous_month_date.replace(day=1)
    end_of_month = previous_month_date.replace(
        day=calendar.monthrange(previous_month_date.year, previous_month_date.month)[1]
    ) + datetime.timedelta(days=1)

    return start_of_month, end_of_month


def caching_instance_data(query_name, query, clear_cache_date):
    """
    Caches queries, that calculate particular instance data,
    including long time unchangeable as like as monthly statistics.

    Arguments:
        query_name (str): Name of query.
        query (query result): Django-query.
        clear_cache_date (date): Last date of saving cache data.

    Returns cached query result.
    """
    if datetime.date.today() == clear_cache_date:
        cache.delete(query_name)

    cached_query = cache.get(query_name)

    if cached_query is not None:
        return cached_query

    cache.set(query_name, query)

    return query
