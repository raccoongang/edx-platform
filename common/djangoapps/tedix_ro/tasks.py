from datetime import datetime
from urlparse import urljoin

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import ugettext as _

from celery.schedules import crontab
from celery.task import periodic_task, task
from edxmako.shortcuts import render_to_string
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import pytz
from xmodule.modulestore.django import modulestore

from .models import StudentCourseDueDate
from .utils import report_data_preparation


@periodic_task(run_every=crontab(hour='10', minute='30'))
def send_teacher_extended_reports():
    for user in User.objects.filter(is_staff=True):
        if hasattr(user, 'instructorprofile'):
            lesson_reports = []
            for enrollment in user.courseenrollment_set.all():
                course = modulestore().get_course(enrollment.course_id)
                report_data = []
                for student_profile in user.instructorprofile.students.filter(user__courseenrollment__course_id=course.id):
                    header, user_data = report_data_preparation(student_profile.user, course, course.id)
                    report_data.append(user_data)
                lesson_reports.append({
                    'course': course,
                    'header': header,
                    'report_data': report_data,
                    'report_url': urljoin(
                        configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                        reverse('extended_report', kwargs={'course_key': course.id})
                    )
                })
            context = {
                'student': user,
                'lesson_reports': lesson_reports
            }
            html_message = render_to_string(
                'emails/extended_report_mail.html',
                context
            )
            txt_message = render_to_string(
                'emails/extended_report_mail.txt',
                context
            )
            from_address = configuration_helpers.get_value(
                'email_from_address',
                settings.DEFAULT_FROM_EMAIL
            )
            send_mail('teacher extended report', txt_message, from_address, [user.email], html_message=html_message)


@periodic_task(run_every=crontab(hour='10', minute='30'))
def send_extended_reports_by_deadline():
    for due_date in StudentCourseDueDate.objects.filter(due_date__lt=datetime.utcnow().replace(tzinfo=pytz.UTC)):
        send_student_extended_reports(due_date.student.user.id, str(due_date.course_id))


@task
def send_student_extended_reports(user_id, course_id):
    user = User.objects.get(pk=user_id)
    if hasattr(user, 'studentprofile'):
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        header, user_data = report_data_preparation(user, course, course_key)
        lesson_reports = [{
                'course': course,
                'report_data': [user_data,],
                'report_url': urljoin(
                    configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                    reverse('extended_report', kwargs={'course_key': course.id})
                )
            }]
        context = {
            'student': user,
            'lesson_reports': lesson_reports
        }
        html_message = render_to_string(
            'emails/extended_report_mail.html',
            context
        )
        txt_message = render_to_string(
            'emails/extended_report_mail.txt',
            context
        )
        from_address = configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL
        )
        send_mail('student extended report', txt_message, from_address, [user.email], html_message=html_message)
