"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""
import json
import requests

from celery.task import task

from lms.envs.devstack_with_worker import PERIODIC_TASK_POST_URL, PLATFORM_LATITUDE, PLATFORM_LONGITUDE, SITE_NAME
from xmodule.modulestore.django import modulestore
from student.models import UserProfile
from .models import TokenStorage


@task
def count_data():
    """
    Periodic task function that gathers information about the students amount,
    geographical coordinates of the platform, courses amount and
    makes a POST request with the data to the appropriate service.
    """

    # Get IP address of the platform and convert it to latitude, longitude.
    check_ip_url = 'http://freegeoip.net/json'
    ip_data = requests.get(check_ip_url)
    ip_data_json = json.loads(ip_data.text)
    if PLATFORM_LATITUDE and PLATFORM_LONGITUDE:
        latitude = PLATFORM_LATITUDE
        longitude = PLATFORM_LONGITUDE
    else:
        latitude = ip_data_json['latitude']
        longitude = ip_data_json['longitude']

    # Get students amount within current platform.
    students_amount = UserProfile.objects.count()

    # Get courses amount within current platform.
    courses_amount = len(modulestore().get_courses())

    # Secret token to authorize our platform on remote server.
    secret_token, created = TokenStorage.objects.get_or_create(pk=1)

    # Posting data to receiving server.
    data_to_send = requests.post(PERIODIC_TASK_POST_URL, data={
        'courses_amount': courses_amount,
        'students_amount': students_amount,
        'latitude': latitude,
        'longitude': longitude,
        'platform_url': SITE_NAME,
        'secret_token': secret_token.secret_token
        })
