import requests
import json
from celery.task import task
from student.models import UserProfile


@task(ignore_result=True)
def count_students():
    students_amount = UserProfile.objects.count()
    r = requests.post('http://requestb.in/ptejf9pt', data=json.dumps({'number_of_students': students_amount}))
    return r
