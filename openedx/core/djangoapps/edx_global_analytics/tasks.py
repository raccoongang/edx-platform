"""
This file contains periodic tasks for edx_global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""

import json
import logging

from celery.task import task
from django.conf import settings
from django.contrib.sites.models import Site
from xmodule.modulestore.django import modulestore


from openedx.core.djangoapps.edx_global_analytics.utils.cache_utils import (
    get_cache_week_key,
    get_cache_month_key,
)
from openedx.core.djangoapps.edx_global_analytics.utils.token_utils import get_acceptor_api_access_token
from openedx.core.djangoapps.edx_global_analytics.utils.utils import (
    fetch_instance_information,
    get_previous_day_start_and_end_dates,
    get_previous_week_start_and_end_dates,
    get_previous_month_start_and_end_dates,
    platform_coordinates,
    send_instance_statistics_to_acceptor,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def paranoid_level_statistics_bunch():
    """
    Gather particular bunch of instance data called `Paranoid`, that contains active students amount
    for day, week and month.
    """
    active_students_amount_day = fetch_instance_information(
        'active_students_amount', get_previous_day_start_and_end_dates(), name_to_cache=None
    )

    active_students_amount_week = fetch_instance_information(
        'active_students_amount', get_previous_week_start_and_end_dates(), name_to_cache=get_cache_week_key()
    )

    active_students_amount_month = fetch_instance_information(
        'active_students_amount', get_previous_month_start_and_end_dates(), name_to_cache=get_cache_month_key()
    )

    return active_students_amount_day, active_students_amount_week, active_students_amount_month


def enthusiast_level_statistics_bunch():
    """
    Gather particular bunch of instance data called `Enthusiast`, that contains students per country amount.
    """
    students_per_country = fetch_instance_information(
        'students_per_country', get_previous_day_start_and_end_dates(), name_to_cache=None,
    )

    return students_per_country


def get_olga_acceptor_url(olga_settings):
    """
    Return OLGA acceptor url that edX application needs to send statistics to.
    """
    acceptor_url = olga_settings.get('ACCEPTOR_URL')
    acceptor_url_develop = olga_settings.get('ACCEPTOR_URL_DEVELOP')

    olga_acceptor_url = acceptor_url or acceptor_url_develop

    if not olga_acceptor_url:
        logger.info('No OLGA periodic task URL.')
        return

    return olga_acceptor_url


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

    olga_acceptor_url = get_olga_acceptor_url(olga_settings)

    access_token = get_acceptor_api_access_token(olga_acceptor_url)

    if not access_token:
        logger.info('Access token was unsuccessfully authorized. Task will try to register a new token in next turn.')
        return

    # Data volume depends on server settings.
    statistics_level = olga_settings.get("STATISTICS_LEVEL")

    courses_amount = len(modulestore().get_courses())

    (active_students_amount_day,
     active_students_amount_week,
     active_students_amount_month) = paranoid_level_statistics_bunch()

    # Paranoid statistics level basic data.
    data = {
        'access_token': access_token,
        'active_students_amount_day': active_students_amount_day,
        'active_students_amount_week': active_students_amount_week,
        'active_students_amount_month': active_students_amount_month,
        'courses_amount': courses_amount,
        'statistics_level': 'paranoid',
    }

    if statistics_level == 'enthusiast':
        platform_url = "https://" + settings.SITE_NAME
        platform_name = settings.PLATFORM_NAME or Site.objects.get_current()
        platform_city_name = olga_settings.get("PLATFORM_CITY_NAME")

        latitude, longitude = platform_coordinates(platform_city_name)

        students_per_country = enthusiast_level_statistics_bunch()

        data.update({
            'latitude': latitude,
            'longitude': longitude,
            'platform_name': platform_name,
            'platform_url': platform_url,
            'statistics_level': 'enthusiast',
            'students_per_country': json.dumps(students_per_country),
        })

    send_instance_statistics_to_acceptor(olga_acceptor_url, data)
