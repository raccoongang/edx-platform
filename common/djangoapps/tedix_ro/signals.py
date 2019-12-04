import logging

from django.dispatch import Signal, receiver
from opaque_keys.edx.keys import CourseKey

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.core.djangoapps.signals.signals import COURSE_GRADE_NOW_PASSED

from .models import Question
from .tasks import send_student_extended_reports
from .utils import lesson_complite

log = logging.getLogger(__name__)


VIDEO_LESSON_COMPLETED = Signal(
    providing_args=[
        'user',  # user object
        'course_id',  # course.id
    ]
)


@receiver(COURSE_GRADE_NOW_PASSED, dispatch_uid="send_student_extended_reports")
def _listen_for_completed_course(sender, user, course_id, **kwargs):
    if lesson_complite(user, course_id):
        send_student_extended_reports.delay(user.id, str(course_id))


@receiver(VIDEO_LESSON_COMPLETED, dispatch_uid="send_student_extended_reports")
def _listen_for_video_lesson_update(sender, user, course_id, **kwargs):
    course_key = CourseKey.from_string(course_id)
    if lesson_complite(user, course_key):
        send_student_extended_reports.delay(user.id, course_id)
