"""
This file contains periodic tasks for global_statistics, which will collect data about Open eDX users
and send this data to appropriate service for further processing.
"""
# import json

import requests
from celery.task import task

from student.models import UserProfile
from lms.envs.devstack_with_worker import PERIODIC_TASK_POST_URL


@task(ignore_result=True)
def count_students():
    """
    Function that gathers information about the students amount and
    makes a post request with the data to the appropriate service.
    """
    students_amount = UserProfile.objects.count()
    data_to_send = requests.post(PERIODIC_TASK_POST_URL, json={'number_of_students': students_amount})
