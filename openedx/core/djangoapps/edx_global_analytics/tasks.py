"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""

import datetime
import pytz
from calendar import monthrange
import json

import requests
from celery.task import task

from django.core.cache import cache
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Count
from django.db.models import Q

from xmodule.modulestore.django import modulestore
from student.models import UserProfile
from .models import TokenStorage


UTC = pytz.UTC


def calculate_active_students_amount(query_name, activity_period):
    """
    Calculates instance active students amount for particular period as like as previous calendar day,
    week and month after cached.
    """

    period_start, period_end = activity_period

    active_students_amount = UserProfile.objects.exclude(
        Q(user__last_login=None) | Q(user__is_active=False)
    ).filter(user__last_login__gt=period_start, user__last_login__lt=period_end).count()

    active_students_amount_after_cached = caching_instance_data(query_name, active_students_amount)

    return active_students_amount_after_cached


def calculate_students_per_country(query_name, activity_period):
    """
    Calculates instance students per country amount for particular period as like as previous calendar day,
    week and month after cached.

    Returns:
        students_per_country_after_cached (dict): Country-count accordance as pair of key-value.
                                                  Example: {u'FR': 3434, u'UA': 1124, None: 2345}
    """

    period_start, period_end = activity_period

    students_per_country = dict(UserProfile.objects.exclude(
        Q(user__last_login=None) | Q(user__is_active=False)
    ).filter(user__last_login__gt=period_start, user__last_login__lt=period_end
    ).values('country').annotate(count=Count('country')).values_list('country', 'count'))

    students_per_country_after_cached = caching_instance_data(query_name, students_per_country)

    return students_per_country_after_cached


def get_previous_day_start_and_end_dates():
    """
    Get accurate date and time of previous calendar day`s start and end.

    Returns:
        start_of_day (datetime): Previous day`s start. Example for 2017-05-15 is 2017-05-14 00:00:00.
        end_of_day (datetime): Previous day`s end. Example for 2017-05-15 is 2017-05-14 23:59:59.
    """

    previous_day = datetime.datetime.today() - datetime.timedelta(days=1)
    start_of_day = previous_day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = previous_day.replace(hour=23, minute=59, second=59, microsecond=59)

    return start_of_day, end_of_day


def get_previous_week_start_and_end_dates():
    """
    Get accurate first and last days (with time) of calendar week.

    Returns:
        start_of_week (datetime): Previous week`s first day start. Example for 2017-05-15 is 2017-05-08 00:00:00.
        end_of_week (datetime): Previous week`s last day end. Example for 2017-05-15 is 2017-05-14 23:59:59.
    """

    days_after_week_started = datetime.datetime.today().weekday() + 7

    start_of_week = (datetime.datetime.today() - datetime.timedelta(
        days=days_after_week_started
    )).replace(hour=0, minute=0, second=0, microsecond=0)

    end_of_week = start_of_week + datetime.timedelta(days=7, seconds=-1)

    return start_of_week, end_of_week


def get_previous_month_start_and_end_dates():
    """
    Get accurate first and last days (with time) of calendar month.

    Returns:
        start_of_month (datetime): Previous month`s first day start. Example for may is 2017-04-01 00:00:00.
        end_of_month (datetime): Previous month`s last day end. Example for may is 2017-04-30 23:59:59.
    """

    last_day_of_previous_month = (datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)).replace(
        tzinfo=UTC
    )

    _, days_in_month = monthrange(last_day_of_previous_month.year, last_day_of_previous_month.month)

    start_of_month = (last_day_of_previous_month - datetime.timedelta(days=days_in_month-1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    end_of_month = last_day_of_previous_month.replace(
        hour=23, minute=59, second=59, microsecond=59
    )

    return start_of_month, end_of_month


def caching_instance_data(query_name, query):
    """
    Caches queries, that calculate particular instance data,
    including long time unchangeable as like as monthly statistics.

    Arguments:
        query_name (str): Name of query.
        query (query result): Django-query.

    Returns cached query result.
    """

    cached_query = cache.get(query_name)

    if cached_query is not None:
        return cached_query

    cache.set(query_name, query)

    return query


@task
def count_data():
    """
    Periodic task function that gathers information about the students amount,
    geographical coordinates of the platform, courses amount and
    makes a POST request with the data to the appropriate service.
    """

    # OLGA settings
    olga_settings = settings.ENV_TOKENS.get('OPENEDX_LEARNERS_GLOBAL_ANALYTICS')

    # Get IP address of the platform and convert it to latitude, longitude.
    ip_data = requests.get('http://freegeoip.net/json')
    ip_data_json = json.loads(ip_data.text)

    platform_latitude = olga_settings.get("PLATFORM_LATITUDE")
    platform_longitude = olga_settings.get("PLATFORM_LONGITUDE")
   
    if platform_latitude and platform_longitude:
        latitude, longitude = platform_latitude, platform_longitude
    else:
        latitude, longitude = ip_data_json['latitude'], ip_data_json['longitude']

    # Aggregated students per country
    students_per_country = calculate_students_per_country(
        'students_per_country', get_previous_month_start_and_end_dates()
    )

    # Get count of active students per previous day, previous calendar week and month
    active_students_amount_day = calculate_active_students_amount(
        'active_students_amount_day', get_previous_day_start_and_end_dates()
    )

    active_students_amount_week = calculate_active_students_amount(
        'active_students_amount_week', get_previous_week_start_and_end_dates()
    )

    active_students_amount_month = calculate_active_students_amount(
        'active_students_amount_month', get_previous_month_start_and_end_dates()
    )

    # Get courses amount within current platform.
    courses_amount = len(modulestore().get_courses())

    # Secret token to authorize our platform on remote server.
    try:
        token_object = TokenStorage.objects.first()
        secret_token = token_object.secret_token
    except AttributeError:
        secret_token = ""

    # Current edx-platform URL
    platform_url = "https://" + settings.SITE_NAME

    # Predefined in the server settings url to send collected data to.
    # For production development.
    if olga_settings.get('OLGA_PERIODIC_TASK_POST_URL'):
        post_url = olga_settings.get('OLGA_PERIODIC_TASK_POST_URL')
    # For local development.
    else:
        post_url = olga_settings.get('OLGA_PERIODIC_TASK_POST_URL_LOCAL')

    # Posts desired data volume to receiving server.
    # Data volume depends on server settings.
    statistics_level = olga_settings.get("STATISTICS_LEVEL")
    
    # Platform name.
    if settings.PLATFORM_NAME:
        platform_name = settings.PLATFORM_NAME
    else:
        platform_name = Site.objects.get_current()

    # Sending instance data
    # Paranoid level basic data
    data = {
        'active_students_amount_day': active_students_amount_day,
        'active_students_amount_week': active_students_amount_week,
        'active_students_amount_month': active_students_amount_month,
        'courses_amount': courses_amount,
        'statistics_level': 'paranoid',
        'secret_token': secret_token
    }

    # Enthusiast level
    if statistics_level == 1:
        data.update({
            'latitude': latitude,
            'longitude': longitude,
            'platform_name': platform_name,
            'platform_url': platform_url,
            'statistics_level': 'enthusiast',
            'students_per_country': json.dumps(students_per_country)
        })

    requests.post(post_url, data)
