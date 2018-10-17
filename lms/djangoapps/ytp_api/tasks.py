"""
Asynchronous tasks for the YTP custom notifier app.
"""
from datetime import timedelta
import logging
import urlparse

from celery.task import periodic_task
from django.conf import settings
from django.core.cache import cache
import requests
from simplejson import JSONDecodeError

from ytp_api.backends.tracking import YTP_TRACKER_CACHE_KEY_ENROLLMENTS, YTP_TRACKER_CACHE_KEY_SUBMISSIONS

log = logging.getLogger(__name__)


def send_statistic_list(items_ids, endpoint):
    url = urlparse.urljoin(getattr(settings, 'ASU_API_URL', ''), endpoint)
    statistic_list = []
    for record_id in items_ids:
        data = cache.get(record_id)
        if not data:
            log.warning("Can not find record wit key `%s` inside cache", record_id)
            continue
        body = data['body']

        statistic_list.append(body)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic {}'.format(getattr(settings, 'ASU_API_KEY', '')),
    }
    log.debug("Headers: %s, URL: %s", headers, url)
    log.info("sending statistic to server :: " + str(statistic_list))
    result = requests.post(url, json=statistic_list, headers=headers)
    try:
        data = result.json()
    except JSONDecodeError:
        data = ''
    log.info("Server response with the code: %s and body: %s", result.status_code, data)
    if str(result.status_code).startswith('20'):
        for record_id in items_ids:
            cache.delete(record_id)


@periodic_task(run_every=timedelta(seconds=getattr(settings, 'ASU_TRACKER_BUFFER_LIFE_TIME', 60)))
def send_statistic():
    batch_size = getattr(settings, 'ASU_TRACKER_BUFFER_SIZE', 60)
    for cache_key, endpoint in [
        (YTP_TRACKER_CACHE_KEY_ENROLLMENTS, getattr(settings, 'ASU_API_ENDPOINT_ENROLLMENTS', '')),
        (YTP_TRACKER_CACHE_KEY_SUBMISSIONS, getattr(settings, 'ASU_API_ENDPOINT_SUBMISSIONS', '')),
    ]:

        records = cache.get(cache_key)
        if records:
            records = list(records)
            for i in xrange(0, len(records), batch_size):
                send_statistic_list(records[i:i + batch_size], endpoint)
            cache.delete(cache_key)
