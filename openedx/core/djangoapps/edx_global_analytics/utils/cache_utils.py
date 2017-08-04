"""
Cache functionality.
"""

from datetime import date, timedelta

from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q
from student.models import UserProfile


def cache_instance_data(name_to_cache, query_type, activity_period):
    """
    Cache queries, that calculate particular instance data with week and month activity period value.

    Arguments:
        name_to_cache (str): year-week or year-month accordance as string.
        query_result (query result): Django-query result.

    Returns cached query result.
    """
    cached_query_result = cache.get(name_to_cache)

    if cached_query_result is not None:
        return cached_query_result

    query_result = get_query_result(query_type, activity_period)
    cache.set(name_to_cache, query_result)

    return query_result


def get_cache_week_key():
    """
    Return previous week `year` and `week` numbers as unique string key for cache.
    """
    previous_week = date.today() - timedelta(days=7)
    year, week_number, _ = previous_week.isocalendar()

    return '{0}-{1}-week'.format(year, week_number)


def get_cache_month_key():
    """
    Return previous month `year` and `month` numbers as unique string key for cache.
    """
    current_month_days_count = date.today().day
    previous_month = (date.today() - timedelta(days=current_month_days_count))

    month_number = previous_month.month
    year = previous_month.year

    return '{0}-{1}-month'.format(year, month_number)


def get_query_result(query_type, activity_period):
    """
    Return query result per query type.
    """
    period_start, period_end = activity_period

    if query_type == 'active_students_amount':
        return UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

    if query_type == 'students_per_country':
        return dict(
            UserProfile.objects.exclude(
                Q(user__last_login=None) | Q(user__is_active=False)
            ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).values(
                'country'
            ).annotate(count=Count('country')).values_list('country', 'count')
        )
