import logging

from django.dispatch import Signal, receiver

from openedx.core.djangoapps.signals.signals import COURSE_GRADE_NOW_PASSED

from .tasks import send_student_complited_report

log = logging.getLogger(__name__)


VIDEO_LESSON_COMPLETED = Signal(
    providing_args=[
        'user',  # user object
        'course_id',  # course.id
    ]
)


@receiver(COURSE_GRADE_NOW_PASSED, dispatch_uid="send_student_extended_reports")
def _listen_for_completed_course(sender, user, course_id, **kwargs):
    send_student_complited_report.delay(user.id, str(course_id))


@receiver(VIDEO_LESSON_COMPLETED, dispatch_uid="send_student_extended_reports")
def _listen_for_video_lesson_update(sender, user, course_id, **kwargs):
    send_student_complited_report.delay(user.id, course_id)
