"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""
import json

import requests
from celery.task import task

from student.models import UserProfile
from lms.envs.devstack_with_worker import PERIODIC_TASK_POST_URL


@task
def count_students():
    """
    Function that gathers information about the students amount, geo-coordinates, courses amount and
    makes a post request with the data to the appropriate service.
    """
    check_ip_url = 'http://freegeoip.net/json'
    ip_data = requests.get(check_ip_url)
    ip_data_json = json.loads(ip_data.text)
    latitude = ip_data_json['latitude']
    longitude = ip_data_json['longitude']
    students_amount = UserProfile.objects.count()
    data_to_send = requests.post(PERIODIC_TASK_POST_URL, data={
    	'students_amount': students_amount,
    	'latitude': latitude,
    	'longitude': longitude
    	})
