"""
Catch changes in user progress and send it by API
"""
import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from opaque_keys.edx.keys import CourseKey
from tasks import send_api_request
from certificates.models import CertificateStatuses
from referrals.models import ActivatedLinks


@receiver(post_save, sender='courseware.StudentModule')
def send_achievement(sender, instance, **kwargs):
    # Remove check for GAMMA_ALLOWED_USERS after release
    if instance.module_type in ('video', 'problem'):
        if (
            instance.module_type == 'video' and
            (instance.modified - instance.created).total_seconds() <= 1
        ):
            return None
        if (
            instance.module_type == 'problem' and
            (not instance.grade or type(instance.grade) != float)
        ):
            return None
        data = {
            'username': instance.student.username,
            'course_id': unicode(instance.course_id),
            'org': instance.course_id.org,
            'event_type': instance.module_type,
            'uid': unicode(instance.module_state_key),
        }
        send_api_request.delay(data)


@receiver(post_save, sender='student.CourseEnrollment')
def send_enroll_achievement(sender, instance, created, **kwargs):
    # Remove check for GAMMA_ALLOWED_USERS after release
    if created and instance.is_active:
        org = instance.course_id.org
        course_id = unicode(instance.course_id)
        data = {
            'username': instance.user.username,
            'course_id': course_id,
            'org': org,
            'event_type': 'enrollment',
            'uid': '{}_{}'.format(instance.user.pk, course_id),
        }
        send_api_request.delay(data)

        activated_link = ActivatedLinks.objects.filter(
            user=instance.user,
            referral__course_id=CourseKey.from_string(course_id),
            used=False
        ).first()
        if activated_link:
            uid = '{}_{}_{}'.format(
                activated_link.referral.user.pk,
                activated_link.referral.course_id,
                'referrer'
            )
            data = {
                'username': activated_link.referral.user.username,
                'course_id': course_id,
                'org': org,
                'event_type': 'referrer',
                'uid': uid
            }
            send_api_request.delay(data)
            activated_link.used = True
            # TODO uncomment this after debug finishing
            # activated_link.save()


@receiver(post_save, sender='certificates.GeneratedCertificate')
def send_certificate_generation(sender, instance, created, **kwargs):
    # Remove check for GAMMA_ALLOWED_USERS after release
    if instance.status in CertificateStatuses.PASSED_STATUSES:
        org = instance.course_id.org
        course_id = unicode(instance.course_id)
        data = {
            'username': instance.user.username,
            'course_id': course_id,
            'org': org,
            'event_type': 'course',
            'uid': '{}_{}'.format(instance.user.pk, course_id),
        }
        
        send_api_request.delay(data)

