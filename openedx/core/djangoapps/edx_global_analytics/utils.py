"""
Helpers for the edX global analytics application.
"""

import calendar
import datetime
import logging

import requests

from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q

from student.models import UserProfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_instance_information(name_to_cache, query_type, activity_period, cache_timeout=None):
    """
    Calculates instance information corresponding for particular period as like as previous calendar day and
    statistics type as like as students per country after cached if needed.
    """
    period_start, period_end = activity_period

    statistics_queries = {
        'active_students_amount': UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count(),

        'students_per_country': dict(
            UserProfile.objects.exclude(
                Q(user__last_login=None) | Q(user__is_active=False)
            ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).values(
                'country'
            ).annotate(count=Count('country')).values_list('country', 'count')
        )
    }

    if cache_timeout is not None:
        return cache_instance_data(name_to_cache, statistics_queries[query_type], cache_timeout)

    return statistics_queries[query_type]


def cache_instance_data(name_to_cache, query_result, cache_timeout):
    """
    Caches queries, that calculate particular instance data,
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

    cache.set(name_to_cache, query_result, cache_timeout)

    return query_result


def cache_timeout_week():
    """
    Calculates how much time cache need to save data for weekly statistics.
    """
    current_datetime = datetime.datetime.now()

    days_after_week_started = datetime.date.today().weekday()

    last_datetime_of_current_week = (current_datetime + datetime.timedelta(
        6 - days_after_week_started)
    ).replace(hour=23, minute=59, second=59)

    cache_timeout_week_in_seconds = (last_datetime_of_current_week - current_datetime).total_seconds()

    return cache_timeout_week_in_seconds


def cache_timeout_month():
    """
    Calculates how much time cache need to save data for monthly statistics.
    """
    current_datetime = datetime.datetime.now()

    last_datetime_of_current_month = current_datetime.replace(
        day=calendar.monthrange(current_datetime.year, current_datetime.month)[1]
    ).replace(hour=23, minute=59, second=59)

    cache_timeout_month_in_seconds = (last_datetime_of_current_month - current_datetime).total_seconds()

    return cache_timeout_month_in_seconds


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


def get_coordinates_by_ip():
    """
    Gather coordinates by server IP address with FreeGeoIP service.
    """
    try:
        ip_data = requests.get('https://freegeoip.net/json')
        latitude, longitude = ip_data.json()['latitude'], ip_data.json()['longitude']
        return latitude, longitude

    except requests.RequestException as error:
        logger.exception(error.message)
        return '', ''


def get_coordinates_by_platform_city_name(city_name):
    """
    Gather coordinates by platform city name with Google API.
    """
    google_api_request = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json', params={'address': city_name}
    )

    coordinates_result = google_api_request.json()['results']

    if coordinates_result:
        location = coordinates_result[0]['geometry']['location']
        return location['lat'], location['lng']


def platform_coordinates(city_name):
    """
    Method gets platform city latitude and longitude.

    If `city_platform_located_in` (name of city) exists in OLGA setting (lms.env.json) as manual parameter
    Google API helps to get city latitude and longitude. Else FreeGeoIP gathers latitude and longitude by IP address.

    All correct city names are available from Wikipedia -
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

    Module `pytz` also has list of cities with `pytz.all_timezones`.
    """
    return get_coordinates_by_platform_city_name(city_name) or get_coordinates_by_ip()
