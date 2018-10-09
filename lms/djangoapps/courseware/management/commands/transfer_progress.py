from logging import getLogger
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Func, Value
from courseware.models import StudentModule
from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

log = getLogger(__name__)

class Command(BaseCommand):
    args = "<old_course_id> <new_course_id> [student_email]"

    def handle(self, *args, **options):
        user = None
        old_course_filter = {}
        new_course_filter = {}
        old_module_filter = {}
        new_module_filter = {}
        if len(args) < 2 or filter(lambda s: not s.startswith('course-v1:'), args[:2]):
            raise CommandError('Must specify old_course_id and new_course_id: e.g. '
                               'course-v3:edX+DemoX+Demo_Course course-v1:edX+DemoX+Demo_Course_T1')
        if len(args) == 3:
            try:
                student_email = args[2]
                validate_email(student_email)
                user = User.objects.get(email=student_email)
            except (ValidationError, User.DoesNotExist):
                raise CommandError('Invalid email {email_address} '
                                   'or user does not exists.'.format(email_address=args[2]))

        old, new = map(CourseKey.from_string, args[:2])
        if old == new:
            raise CommandError('Different course-id must be specified')
        if not modulestore().get_course(old):
            raise CommandError('Course {course} does not exists.'.format(course=old))
        if not modulestore().get_course(new):
            raise CommandError('Course {course} does not exists.'.format(course=new))

        old_course_filter['course_id'] = old_module_filter['course_id'] = old
        new_course_filter['course_id'] = new_module_filter['course_id'] = new

        if user:
            old_course_filter['user_id'] = old_module_filter['student_id'] = user.id
            new_course_filter['user_id'] = new_module_filter['student_id'] = user.id

        if CourseEnrollment.objects.filter(**old_course_filter).exists() and \
            StudentModule.objects.filter(**old_module_filter):
            log.info('Transfering course progress...')
            CourseEnrollment.objects.filter(**new_course_filter).delete()
            CourseEnrollment.objects.filter(**old_course_filter).update(course_id=new)
            StudentModule.objects.filter(**new_module_filter).delete()
            StudentModule.objects.filter(**old_module_filter).update(
                course_id=new,
                module_state_key=Func(
                    F('module_state_key'),
                    Value('block-v1:{}'.format(old.to_deprecated_string()[10:])),
                    Value('block-v1:{}'.format(new.to_deprecated_string()[10:])),
                    function='replace',
                )
            )
            log.info('Done')
        else:
            log.info('There is no enrollments or any progress on '
                     'course {course}{for_student}'.format(
                         course=old, for_student=" for student with id "+str(user.id) if user else "")
                    )
