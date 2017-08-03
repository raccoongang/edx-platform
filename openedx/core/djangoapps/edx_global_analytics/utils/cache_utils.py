"""
Cache functionality.
"""

from datetime import date, timedelta

from django.core.cache import cache


def cache_instance_data(name_to_cache, query_result):
    """
    Cache queries, that calculate particular instance data,
    including long time unchangeable weekly and monthly statistics.

    Arguments:
        name_to_cache (str): Name of query.
        query_result (query result): Django-query result.
        cache_timeout (int/None): Caching for particular seconds amount.

    Returns cached query result.
    """
    cached_query_result = cache.get(name_to_cache)

    if cached_query_result is not None:
        return cached_query_result

    cache.set(name_to_cache, query_result)

    return query_result


def get_cache_week_key():
    """
    Return year and week number of previous week as unique string key for cache.
    """
    year, week_number, _ = (date.today() - timedelta(days=7)).isocalendar()
    return '%s-%s'.format(year, week_number)


def get_cache_month_key():
    """
    Return year and month number of previous week as unique string key for cache.
    """
    previous_month = (date.today() - timedelta(days=date.today().day))
    month_number = previous_month.month
    year = previous_month.year

    return '%s-%s'.format(year, month_number)
