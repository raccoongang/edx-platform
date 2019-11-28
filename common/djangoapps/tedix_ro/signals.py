import logging

from django.dispatch import receiver

from openedx.core.djangoapps.signals.signals import COURSE_GRADE_NOW_PASSED

from .tasks import send_student_extended_reports


log = logging.getLogger(__name__)


@receiver(COURSE_GRADE_NOW_PASSED, dispatch_uid="send_student_extended_reports")
def _listen_for_completed_course(sender, user, course_id, **kwargs):
    send_student_extended_reports.delay(user.id, str(course_id))
