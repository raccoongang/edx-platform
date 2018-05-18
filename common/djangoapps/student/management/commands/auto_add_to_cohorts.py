import branding

from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey

from student.models import CourseEnrollment, _automatic_add_user_to_cohort


class Command(BaseCommand):
    help = "This command will automatically add the users to gender cohorts"

    def handle(self, *args, **options):
        course_ids = [CourseKey.from_string(str(c.id)) for c in branding.get_visible_courses()]
        course_enrollments = CourseEnrollment.objects.filter(course_id__in=course_ids)

        for course_enrollment in course_enrollments:
            _automatic_add_user_to_cohort(course_enrollment.course_id, course_enrollment.user)

        print "Success!"