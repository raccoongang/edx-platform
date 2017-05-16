"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""

import json

import requests
from celery.task import task

from django.conf import settings
from django.contrib.sites.models import Site

from xmodule.modulestore.django import modulestore
from .models import TokenStorage

from .utils import calculate_active_students_amount, calculate_students_per_country, \
                    get_previous_day_start_and_end_dates, get_previous_week_start_and_end_dates, \
                    get_previous_month_start_and_end_dates


def calculate_instance_information():
    """
    Calculates overall information about instance.

    Returns:
        active_students_amount_day (int): Active students amount per last calendar day.
        active_students_amount_week (int): Active students amount per last calendar week.
        active_students_amount_month (int): Active students amount per last calendar month.
        courses_amount (int): Courses amount.
        students_per_country (dict): Country-count accordance as pair of key-value.
                                     Example: {u'FR': 3434, u'UA': 1124}
    """
    students_per_country = calculate_students_per_country(
        'students_per_country', get_previous_month_start_and_end_dates()
    )

    active_students_amount_day = calculate_active_students_amount(
        'active_students_amount_day', get_previous_day_start_and_end_dates()
    )

    active_students_amount_week = calculate_active_students_amount(
        'active_students_amount_week', get_previous_week_start_and_end_dates()
    )

    active_students_amount_month = calculate_active_students_amount(
        'active_students_amount_month', get_previous_month_start_and_end_dates()
    )

    courses_amount = len(modulestore().get_courses())

    return (active_students_amount_day,
            active_students_amount_week,
            active_students_amount_month,
            courses_amount,
            students_per_country)


def send_instance_information(
        statistics_level, post_url, platform_name, platform_url, latitude, longitude, secret_token,
        active_students_amount_day, active_students_amount_week, active_students_amount_month,
        courses_amount, students_per_country):
    """
    Send information about instance depending on a statistics level.
    Make post-request to independent server, that gathers statistics.
    """

    # Paranoid level basic data.
    data = {
        'active_students_amount_day': active_students_amount_day,
        'active_students_amount_week': active_students_amount_week,
        'active_students_amount_month': active_students_amount_month,
        'courses_amount': courses_amount,
        'statistics_level': 'paranoid',
        'secret_token': secret_token
    }

    # Enthusiast level.
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

    # Get all information, that need to be calculated.
    (active_students_amount_day,
     active_students_amount_week,
     active_students_amount_month,
     courses_amount,
     students_per_country) = calculate_instance_information()

    # Secret token to authorize our platform on remote server.
    try:
        token_object = TokenStorage.objects.first()
        secret_token = token_object.secret_token
    except AttributeError:
        secret_token = ""

    # Current edx-platform URL.
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

    # Send information about instance depending on a statistics level.
    send_instance_information(
        statistics_level, post_url, platform_name, platform_url, latitude, longitude, secret_token,
        active_students_amount_day, active_students_amount_week, active_students_amount_month,
        courses_amount, students_per_country
    )
