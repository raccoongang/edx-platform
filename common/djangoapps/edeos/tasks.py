"""
Edeos related Celery tasks.
"""
import logging
from urlparse import urljoin

from celery.task import task
from django.core.cache import cache

from utils import send_edeos_api_request


log = logging.getLogger(__name__)


@task()
def send_api_request(data):
    """
    Send data to Edeos API.
    """
    send_edeos_api_request(**data)
    # TODO: elaborate on caching rules specific for each event (e.g. based on uid)
    """
    cache_key = '{}:{}:{}'.format(
        data.get('payload', {}).get('student_id'),
        data.get('payload', {}).get('course_id'),
        data.get('payload', {}).get('event_type')
    )
    if not cache.get(cache_key):
        response = send_edeos_api_request(**data)
        if response:
            cache.set(cache_key, True, 30)
    """