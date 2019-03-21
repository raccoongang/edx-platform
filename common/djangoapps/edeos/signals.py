"""
Catch changes in user progress and send it by API
"""
import json
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from opaque_keys.edx.keys import CourseKey
from edeos.tasks import send_api_request
from certificates.models import CertificateStatuses
from referrals.models import ActivatedLinks
from xmodule.modulestore.django import modulestore
from django.contrib.sites.models import Site

edeos_FIELDS = (
    'edeos_base_url',
    'edeos_secret',
    'edeos_key',
)

log = logging.getLogger(__name__)

def _is_valid(fields):
    for field in edeos_FIELDS:
        if not fields.get(field):
            log.error('Field "{}" is improperly configured.'.format(field))
            return False
    return True


@receiver(post_save, sender='student.CourseEnrollment')
def send_enroll_achievement(sender, instance, created, **kwargs):
    org = instance.course_id.org
    course_id = unicode(instance.course_id)
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)
    edeos_fields = {
        'edeos_secret': course.edeos_secret,
        'edeos_key': course.edeos_key,
        'edeos_base_url': course.edeos_base_url
    }
    if course.edeos_enabled:
        if _is_valid(edeos_fields):
            # TODO add other params if needed
            payload = {
                'student_id': instance.user.email,
                'course_id': course_id,
                'org': org,
                'event_type': 1,  # TODO move to some sort of configs
                'uid': '{}_{}'.format(instance.user.pk, course_id),
            }

            data = {
                'payload': payload,
                'secret': course.edeos_secret,
                'key': course.edeos_key,
                'base_url': course.edeos_base_url,
                'api_endpoint': 'transactions_store'
            }
            send_api_request.delay(data)  # TODO change to `apply_async()`
