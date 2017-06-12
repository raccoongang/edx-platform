"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""

import json
import logging

import requests
from celery.task import task

from django.conf import settings
from django.contrib.sites.models import Site

from lms.urls import EDX_GLOBAL_ANALYTICS_APP_URL
from xmodule.modulestore.django import modulestore

from .models import TokenStorage
from .utils import (
    fetch_instance_information,
    get_previous_day_start_and_end_dates,
    get_previous_week_start_and_end_dates,
    get_previous_month_start_and_end_dates,
    cache_timeout_week,
    cache_timeout_month,
    platform_coordinates
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def paranoid_level_statistics_bunch():
    """
    Gathers particular bunch of instance data called `Paranoid`, that contains active students amount
    for day, week and month.
    """
    active_students_amount_day = fetch_instance_information(
        'active_students_amount_day', 'active_students_amount',
        get_previous_day_start_and_end_dates(), cache_timeout=None
    )

    active_students_amount_week = fetch_instance_information(
        'active_students_amount_week', 'active_students_amount',
        get_previous_week_start_and_end_dates(), cache_timeout_week()
    )

    active_students_amount_month = fetch_instance_information(
        'active_students_amount_month', 'active_students_amount',
        get_previous_month_start_and_end_dates(), cache_timeout_month()
    )

    return active_students_amount_day, active_students_amount_week, active_students_amount_month


def enthusiast_level_statistics_bunch():
    """
    Gathers particular bunch of instance data called `Enthusiast`, that contains students per country amount.
    """
    students_per_country = fetch_instance_information(
        'students_per_country', 'students_per_country',
        get_previous_day_start_and_end_dates(), cache_timeout=None
    )

    return students_per_country


@task
def collect_stats():
    """
    Periodic task function that gathers instance information as like as platform name,
    active students amount, courses amount etc., then makes a POST request with the data to the appropriate service.

    Sending information depends on statistics level in settings, that have an effect on bunch of data size.
    """

    if 'OPENEDX_LEARNERS_GLOBAL_ANALYTICS' not in settings.ENV_TOKENS:
        logger.info('No OpenEdX Learners Global Analytics settings in file `lms.env.json`.')
        return

    olga_settings = settings.ENV_TOKENS.get('OPENEDX_LEARNERS_GLOBAL_ANALYTICS')

    try:
        token_object = TokenStorage.objects.first()
        secret_token = token_object.secret_token
    except AttributeError:
        secret_token = ""

    platform_url = "https://" + settings.SITE_NAME

    post_url = \
        olga_settings.get('OLGA_PERIODIC_TASK_POST_URL') or olga_settings.get('OLGA_PERIODIC_TASK_POST_URL_LOCAL')

    if not post_url:
        logger.info('No OLGA periodic task post URL.')
        return

    # Data volume depends on server settings.
    statistics_level = olga_settings.get("STATISTICS_LEVEL")

    courses_amount = len(modulestore().get_courses())

    (active_students_amount_day,
     active_students_amount_week,
     active_students_amount_month) = paranoid_level_statistics_bunch()

    # Paranoid level basic data.
    data = {
        'active_students_amount_day': active_students_amount_day,
        'active_students_amount_week': active_students_amount_week,
        'active_students_amount_month': active_students_amount_month,
        'courses_amount': courses_amount,
        'statistics_level': 'paranoid',
        'secret_token': secret_token,

        # Application URL for token authentication flow
        'edx_global_analytics_app_url': EDX_GLOBAL_ANALYTICS_APP_URL,
    }

    # Enthusiast level (extends Paranoid level)
    if statistics_level == 1:

        platform_city_name = olga_settings.get("PLATFORM_CITY_NAME")

        latitude, longitude = platform_coordinates(platform_city_name)

        platform_name = settings.PLATFORM_NAME or Site.objects.get_current()

        students_per_country = enthusiast_level_statistics_bunch()

        data.update({
            'latitude': latitude,
            'longitude': longitude,
            'platform_name': platform_name,
            'platform_url': platform_url,
            'statistics_level': 'enthusiast',
            'students_per_country': json.dumps(students_per_country)
        })

    try:
        request = requests.post(post_url, data)
        logger.info('Connected without error to {0}'.format(request.url))

        if request.status_code == 201:
            logger.info('Data were successfully transferred to OLGA acceptor. Status code is 201.')
        else:
            logger.info('Data were not successfully transferred to OLGA acceptor. Status code is {0}.'.format(
                request.status_code
            ))

    except requests.RequestException as error:
        logger.exception(error.message)
