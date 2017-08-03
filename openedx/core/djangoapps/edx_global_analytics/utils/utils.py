"""
Helpers for the edX global analytics application.
"""

import calendar
import httplib
import logging
from datetime import date, timedelta

import requests
from django.db.models import Count
from django.db.models import Q
from student.models import UserProfile

from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import cache_instance_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_instance_information(query_type, activity_period, name_to_cache=None):
    """
    Calculate instance information corresponding for particular period as like as previous calendar day and
    statistics type as like as students per country after cached if needed.
    """
    query_result = get_query_result(query_type, activity_period)

    print(query_result, type(query_result))

    if name_to_cache is not None:
        return cache_instance_data(name_to_cache, query_result)

    return query_result


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


def get_previous_day_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar day.

    Returns:
        start_of_day (date): Previous day`s start. Example for 2017-05-15 is 2017-05-15.
        end_of_day (date): Previous day`s end, it`s a next day (tomorrow) toward day`s start,
                           that doesn't count in segment. Example for 2017-05-15 is 2017-05-16.
    """
    end_of_day = date.today()
    start_of_day = end_of_day - timedelta(days=1)

    return start_of_day, end_of_day


def get_previous_week_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar week.

    Returns:
        start_of_week (date): Calendar week`s start day. Example for 2017-05-17 is 2017-05-08.
        end_of_week (date): Calendar week`s end day, it`s the first day of next week, that doesn't count in segment.
                             Example for 2017-05-17 is 2017-05-15.
    """
    days_after_week_started = date.today().weekday() + 7

    start_of_week = date.today() - timedelta(days=days_after_week_started)
    end_of_week = start_of_week + timedelta(days=7)

    return start_of_week, end_of_week


def get_previous_month_start_and_end_dates():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar month.

    Returns:
        start_of_month (date): Calendar month`s start day. Example for may is 2017-04-01.
        end_of_month (date): Calendar month`s end day, it`s the first day of next month, that doesn't count in segment.
                             Example for may is 2017-05-01.
    """
    previous_month_date = date.today().replace(day=1) - timedelta(days=1)

    start_of_month = previous_month_date.replace(day=1)
    end_of_month = previous_month_date.replace(
        day=calendar.monthrange(previous_month_date.year, previous_month_date.month)[1]
    ) + timedelta(days=1)

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
    Get platform city latitude and longitude.

    If `city_platform_located_in` (name of city) exists in OLGA setting (lms.env.json) as manual parameter
    Google API helps to get city latitude and longitude. Else FreeGeoIP gathers latitude and longitude by IP address.

    All correct city names are available from Wikipedia -
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

    Module `pytz` also has list of cities with `pytz.all_timezones`.
    """
    return get_coordinates_by_platform_city_name(city_name) or get_coordinates_by_ip()


def request_exception_handler_with_logger(function):
    """
    Request Exception decorator. Logs error message if it exists.
    """
    def request_exception_wrapper(*args, **kwargs):
        """
        Decorator wrapper.
        """
        try:
            return function(*args, **kwargs)
        except requests.RequestException as error:
            logger.exception(error.message)
            return

    return request_exception_wrapper


@request_exception_handler_with_logger
def send_instance_statistics_to_acceptor(olga_acceptor_url, data):
    """
    Dispatch installation statistics OLGA acceptor.
    """
    request = requests.post(olga_acceptor_url + '/api/installation/statistics/', data)
    status_code = request.status_code

    if status_code == httplib.CREATED:
        logger.info('Data were successfully transferred to OLGA acceptor. Status code is {0}.'.format(status_code))
    else:
        logger.info('Data were not successfully transferred to OLGA acceptor. Status code is {0}.'.format(status_code))
