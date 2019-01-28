"""
Helpers for the edX global analytics application.
"""

import calendar
import httplib
import logging
from datetime import date, timedelta

import requests

from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import cache_instance_data, get_query_result

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
    Gather coordinates by server IP address with ip-api service.
    This endpoint is limited to 150 requests per minute from an IP address.
    """
    latitude, longitude = '', ''

    ip_data = requests.get('http://ip-api.com/json')

    if ip_data.status_code == 200:
        latitude, longitude = ip_data.json().get('lat'), ip_data.json().get('lon')

    return latitude, longitude


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
