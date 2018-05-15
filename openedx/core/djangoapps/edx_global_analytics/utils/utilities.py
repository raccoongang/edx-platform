"""
Helpers for the edX global analytics application.
"""

import calendar
import httplib
import logging
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Func, Value

import requests

import lms.djangoapps.certificates as certificates
from certificates.models import GeneratedCertificate
from courseware.courses import get_course_by_id
from courseware.models import StudentModule
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import (
    cache_instance_data,
    get_query_result,
    get_last_analytics_sent_date,
    set_last_analytics_sent_date,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_instance_information(query_type, activity_period, name_to_cache=None):
    """
    Calculate instance information corresponding for particular period as like as previous calendar day and
    statistics type as like as students per country after cached if needed.
    """
    if name_to_cache is not None:
        return cache_instance_data(name_to_cache, query_type, activity_period)

    return get_query_result(query_type, activity_period)


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
        return True
    else:
        logger.info('Data were not successfully transferred to OLGA acceptor. Status code is {0}.'.format(status_code))
        return False


def get_registered_students_daily(token):
    """
    Get registered users count daily starting from the day after the date_start.

    :param token: string of the token that used in cache key creation
    :return: Dictionary where the keys is a dates and the values is the counts.
    """
    last_date = get_last_analytics_sent_date('registered_students', token)
    registered_users = User.objects.filter(date_joined__gt=last_date).annotate(
        date=Func(F('date_joined'), Value('%Y-%m-%d'), function='date_format')
    ).values('date').annotate(count=Count('id'))
    return dict((day['date'], day['count']) for day in registered_users)


def get_generated_certificates_daily(token):
    """
    Get the count of the certificates generated  daily starting from the day after the date_start.

    :param token: string of the token that used in cache key creation
    :param date_start: datetime of the last day analytics was sent for
    :return: Dictionary where the keys is a dates and the values is the counts.
    """
    last_date = get_last_analytics_sent_date('generated_certificates', token)
    generated_certificates = GeneratedCertificate.objects.filter(
        created_date__gt=last_date
    ).annotate(
        date=Func(F('created_date'), Value('%Y-%m-%d'), function='date_format')
    ).values('date').annotate(count=Count('id'))
    return dict((day['date'], day['count']) for day in generated_certificates)


def get_enthusiastic_students_daily(token):
    """
    Get enthusiastic students count daily starting from the day after the date_start.

    :param token: string of the token that used in cache key creation
    :param date_start: datetime of the last day analytics was sent for
    :return: Dictionary where the keys is a dates and the values is the counts.
    """
    last_date = get_last_analytics_sent_date('enthusiastic_students', token)
    last_sections_ids = get_all_courses_last_sections_ids()
    enthusiastic_students = StudentModule.objects.filter(
        created__gt=last_date, module_state_key__in=last_sections_ids
    ).annotate(
        date=Func(F('created'), Value('%Y-%m-%d'), function='date_format')
    ).values('date').annotate(count=Count('student_id'))
    return dict((day['date'], day['count']) for day in enthusiastic_students)


def get_all_courses_last_sections_ids():
    """
    Get ids of all the courses.

    :return: list of the unique courses ids
    """
    courses_ids = CourseOverview.objects.all().values_list('id', flat=True)
    last_sections_ids = []

    for course_id in courses_ids:
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            continue

        course = get_course_by_id(course_key, depth=2)
        last_sections_ids.append(course.get_children()[-1].location)

    return last_sections_ids
