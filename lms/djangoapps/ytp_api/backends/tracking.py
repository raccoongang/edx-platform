from abc import ABCMeta, abstractmethod
import logging

from django.conf import settings
from django.core.cache import cache

from enrollment import data as enrollment_api
from track.backends import BaseBackend

log = logging.getLogger(__name__)

YTP_TRACKER_CACHE_KEY = 'ytp.tracker'
YTP_TRACKER_CACHE_KEY_ENROLLMENTS = '{}.enrollments'.format(YTP_TRACKER_CACHE_KEY)
YTP_TRACKER_CACHE_KEY_SUBMISSIONS = '{}.submissions'.format(YTP_TRACKER_CACHE_KEY)


class StatisticProcessor(object):
    """
    Base class for process statistic item.
    """
    __metaclass__ = ABCMeta

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @abstractmethod
    def is_can_process(self, event):
        """
        Return True if current processor can process task.

        Attention - don`t modify event object
        """
        pass

    @abstractmethod
    def process(self, event):
        """
        Process log event.

        Return dictionary with data, specific for this event.

        Attention - don`t modify event object.
        """
        pass

    def get_event_timestamp_as_string(self, event):
        return (event['time'] if 'time' in event else event['timestamp']).strftime(self.TIME_FORMAT)

    @staticmethod
    def get_event_name(event):
        if 'event_type' in event:
            return event['event_type']
        return event['name']

    @staticmethod
    def get_event_user(event):
        return event.get(
            'username',
            event.get('context', {}).get('username')
        )

    @staticmethod
    def get_event_course_id(event):
        return event.get('context', {}).get('course_id')

    @staticmethod
    def get_event_quizz_name(event):
        return event.get('context', {}).get('module', {}).get('display_name')


class SubmissionStaticsProcessor(StatisticProcessor):
    PAYLOAD_KEYS = ['success', 'grade', 'state', 'attempts', 'max_grade']

    def is_can_process(self, event):
        return self.get_event_name(event) == 'problem_check' and 'event' in event and isinstance(event['event'], dict)

    def process(self, event):
        result = {}
        data = event['event']
        result['course_id'] = self.get_event_course_id(event)
        result['time'] = self.get_event_timestamp_as_string(event)
        result['username'] = self.get_event_user(event)
        result['quizz_name'] = self.get_event_quizz_name(event)
        result.update({k: v for k, v in data.iteritems() if k in self.PAYLOAD_KEYS})
        log.debug("Result payload: %s", result)
        return result


class EnrollmentProcessor(StatisticProcessor):

    DATETIME_COURSE_FIELDS = ('enrollment_start', 'enrollment_end', 'course_start', 'course_end')

    def is_can_process(self, event):
        return self.get_event_name(event) == 'edx.course.enrollment.mode_changed' and 'event' in event

    def process(self, event):
        user_name = self.get_event_user(event)
        course_id = self.get_event_course_id(event)
        result = enrollment_api.get_course_enrollment(user_name, course_id)
        log.debug("Enrollment Data is: %s", result)
        for field in result['course_details']:
            if field in self.DATETIME_COURSE_FIELDS and result['course_details'][field]:
                result['course_details'][field] = result['course_details'][field].strftime(self.TIME_FORMAT)
        return result


class TrackingBackend(BaseBackend):
    cache_lifetime = getattr(settings, 'YTP_CACHE_LIFETIME', 60 * 60 * 24 * 30)

    def __init__(self, **kwargs):
        super(TrackingBackend, self).__init__(**kwargs)

        self.statistic_processors = [
            SubmissionStaticsProcessor(),
            EnrollmentProcessor(),
        ]

    def update_statistic_cache(self, key, tag):
        item = cache.get(key, set())
        item.add(tag)
        cache.set(key, item, self.cache_lifetime)
        log.debug("Cache for key: %s is updated with tag: %s", key, tag)

    def send(self, event):
        username = StatisticProcessor.get_event_user(event)

        if not username:
            return

        for processor in self.statistic_processors:
            if processor.is_can_process(event):
                body = processor.process(event)
                if not body:
                    continue
                course_id = event['context']['course_id']
                problem_id = event['event'].get('problem_id', '')
                if problem_id:
                    body = [body]
                cached_item_tag = '.'.join([YTP_TRACKER_CACHE_KEY, username, course_id, problem_id])
                cached_item = cache.get(cached_item_tag)
                if not cached_item:
                    cached_item = {'body': body, 'username': username, 'course_id': course_id}
                elif problem_id:
                    cached_item['body'].extend(body)
                else:
                    cached_item['body'].update(body)
                log.debug("Cached BODY: %s", cached_item['body'])
                cache.set(cached_item_tag, cached_item, self.cache_lifetime)
                self.update_statistic_cache(
                    YTP_TRACKER_CACHE_KEY_SUBMISSIONS if problem_id else YTP_TRACKER_CACHE_KEY_ENROLLMENTS,
                    cached_item_tag
                )

