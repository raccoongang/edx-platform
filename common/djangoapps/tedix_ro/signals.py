import logging

from django.dispatch import Signal, receiver

from openedx.core.djangoapps.signals.signals import COURSE_GRADE_NOW_PASSED, COURSE_GRADE_CHANGED

from lms.djangoapps.grades.signals.signals import PROBLEM_WEIGHTED_SCORE_CHANGED

from .tasks import send_student_completed_report

log = logging.getLogger(__name__)


VIDEO_LESSON_COMPLETED = Signal(
    providing_args=[
        'user',  # user object
        'course_id',  # course.id
    ]
)


@receiver(PROBLEM_WEIGHTED_SCORE_CHANGED, dispatch_uid="send_student_extended_reports")
def _listen_for_completed_course(sender, **kwargs):
    course_id = kwargs.get('course_id')
    user_id = kwargs.get('user_id')
    course_id and user_id and send_student_completed_report.apply_async(args=(user_id, course_id), countdown=4)


@receiver(VIDEO_LESSON_COMPLETED, dispatch_uid="send_student_extended_reports")
def _listen_for_video_lesson_update(sender, user, course_id, **kwargs):
    send_student_completed_report.delay(user.id, course_id)
