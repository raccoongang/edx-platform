"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""

import datetime
import json

import requests
from celery.task import task

from django.conf import settings
from django.contrib.sites.models import Site
from xmodule.modulestore.django import modulestore

from student.models import UserProfile
from .models import TokenStorage

from django.db.models import Count
from django.db.models import Q


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

    # Get count of active students (if logged in during last 30 days).
    # Built-in edX`s accounts have None in `last_login` field.
    # 30th day <= Current last login date <= Today
    activity_border = (datetime.datetime.now() - datetime.timedelta(days=olga_settings.get("ACTIVITY_PERIOD")))
    active_students_amount = UserProfile.objects.exclude(
        Q(user__last_login=None) | Q(user__is_active=False)).filter(user__last_login__gt=activity_border).count()

    # Aggregated students per country
    students_per_country = UserProfile.objects.exclude(Q(user__last_login=None) | Q(user__is_active=False)).filter(
        user__last_login__gt=activity_border).values('country').annotate(count=Count('country'))

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
    paranoid = {
        'active_students_amount': active_students_amount,
        'courses_amount': courses_amount,
        'statistics_level': 'paranoid',
        'secret_token': secret_token
        }

    # Enthusiast level
    if statistics_level == 1:
        enthusiast = paranoid.copy()
        enthusiast.update({
            'latitude': latitude,
            'longitude': longitude,
            'platform_name': platform_name,
            'platform_url': platform_url,
            'statistics_level': 'enthusiast',
            'students_per_country': json.dumps(list(students_per_country))
        })
        requests.post(post_url, enthusiast)

    # Paranoid level
    elif statistics_level == 2:
        requests.post(post_url, paranoid)
