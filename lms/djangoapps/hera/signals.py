from django.dispatch.dispatcher import receiver
from hera.utils import clear_active_course_cache_for_users
from student.models import CourseEnrollment, CourseEnrollmentAllowed
from xmodule.modulestore.django import SignalHandler


@receiver(SignalHandler.course_deleted)
def listen_for_course_deleted(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    CourseEnrollmentAllowed.objects.filter(course_id=course_key).delete()
    enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    user_ids = [enrollment.user.id for enrollment in enrollments]
    clear_active_course_cache_for_users(user_ids)
    enrollments.delete()
