import logging
from celery.task import task

import requests
from urlparse import urljoin
from django.core.cache import cache


log = logging.getLogger(__name__)


@task()
def send_api_request(data):
    """
    Send data to edeos API
    """
    base_url = urljoin(data.get('base_url'), data.get('path', ''))
    cache_key = '{}:{}:{}'.format(
        data.get('payload', {}).get('student_id'),
        data.get('payload', {}).get('course_id'),
        data.get('payload', {}).get('event_type')
    )

    log.info("Data to be sent - {}".format(data))
    if not cache.get(cache_key):
        response = requests.post(base_url, data=data.get('payload'), headers={
            "HTTP_SECRET": data.get("secret"),
            "HTTP_KEY": data.get("key")
        })
        if response.status_code == 200:
            cache.set(cache_key, True, 30)
        log.info("Edeos response: status - {}, content - {}".format(response.status_code, response.content))
