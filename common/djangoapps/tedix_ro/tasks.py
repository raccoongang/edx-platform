from datetime import datetime, timedelta
from urlparse import urljoin

from babel.dates import format_datetime
from celery.schedules import crontab
from celery.task import periodic_task, task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
import pytz

from edxmako.shortcuts import render_to_string
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from xmodule.modulestore.django import modulestore

from .models import InstructorProfile, StudentCourseDueDate, StudentReportSending
from .sms_client import SMSClient
from .utils import report_data_preparation, lesson_course_grade, video_lesson_complited, all_problems_have_answer


@periodic_task(run_every=crontab(minute='*/5'))
def send_teacher_extended_reports():
    """
    Sends extended report for the teacher with all his courses and all his students
    """
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    for instructor in InstructorProfile.objects.filter(user__is_staff=True).prefetch_related('students'):
        lesson_reports = []
        for enrollment in instructor.user.courseenrollment_set.filter():
            course = modulestore().get_course(enrollment.course_id)
            if course.end and course.end + timedelta(1) < datetime_now:
                continue
            report_data = []
            header = []
            for student_profile in instructor.students.filter(user__courseenrollment__course_id=course.id):
                header, user_data = report_data_preparation(student_profile.user, course)
                report_data.append(user_data)
            if report_data:
                lesson_reports.append({
                    'course_name': course.display_name,
                    'header': header,
                    'report_data': report_data,
                    'report_url': urljoin(
                        configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                        reverse('extended_report', kwargs={'course_key': course.id})
                    )
                })
        if lesson_reports:
            subject = u'{platform_name}: Report for {username}'.format(
                platform_name=settings.PLATFORM_NAME,
                username=instructor.user.profile.name or instructor.user.username
            )
            context = {
                'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                'user': instructor.user,
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
            send_mail(subject, txt_message, from_address, [instructor.user.email], html_message=html_message)


@periodic_task(run_every=crontab(minute='*/5'))
def send_extended_reports_by_deadline():
    """
    Sends an extended report to the student if the course deadline has expired in the last 24 hours
    and the course has not been completed (not all questions have attempts and the course was not passed)
    """
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    for due_date in StudentCourseDueDate.objects.filter(
            due_date__lte=datetime_now,
            due_date__gt=datetime_now-timedelta(1)):
        user = due_date.student.user
        course_id = due_date.course_id
        course_grade = lesson_course_grade(user, course_id)
        if not (course_grade.passed and all_problems_have_answer(user, course_grade)
            and video_lesson_complited(user, course_id)):
            send_student_extended_reports(user.id, str(course_id))


@task
def send_student_complited_report(user_id, course_id):
    """
    Sends an extended report to the student if  questions have attempts and
    the course has been passed and the grade has been raised
    """
    user = User.objects.filter(id=user_id).first()
    if user and hasattr(user, 'studentprofile'):
        course_key = CourseKey.from_string(course_id)
        student_report_sending, created = StudentReportSending.objects.get_or_create(
            course_id=course_key,
            user=user,
            defaults={
                'grade': 0
            }
        )
        course_grade = lesson_course_grade(user, course_key)
        if (video_lesson_complited(user, course_key) and course_grade.passed and
            (created or student_report_sending.grade < course_grade.percent) and
            all_problems_have_answer(user, course_grade)):
            student_report_sending.grade = course_grade.percent
            student_report_sending.save()
            send_student_extended_reports(user_id, course_id)


@task
def send_student_extended_reports(user_id, course_id):
    """
    Sends email and SMS with an extended report for student and his parent
    """
    user = User.objects.filter(id=user_id).first()
    if user and hasattr(user, 'studentprofile'):
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        header, user_data = report_data_preparation(user, course)
        lesson_reports = [{
                'course_name': course.display_name,
                'report_data': [user_data,],
                'report_url': urljoin(
                    configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                    reverse('extended_report', kwargs={'course_key': course.id})
                )
            }]
        subject = u'{platform_name}: Report for {username} on "{course_name}"'.format(
            platform_name=settings.PLATFORM_NAME,
            username=user.profile.name or user.username,
            course_name=course.display_name
        )
        context = {
            'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            'user': user,
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
        parent = user.studentprofile.parents.first()
        send_mail(subject, txt_message, from_address, [user.email, parent.user.email], html_message=html_message)

        student_course_due_date = StudentCourseDueDate.objects.filter(
            student=user.studentprofile,
            course_id=course_key
        ).first()
        if student_course_due_date:
            due_date = format_datetime(student_course_due_date.due_date, "yy.MM.dd hh:mm a", locale='en')
        else:
            due_date = 'N/A'
        context.update({
            'due_date': due_date,
        })
        sms_message = render_to_string(
            'sms/light_report.txt',
            context
        )
        sms_client = SMSClient()
        sms_client.send_message(user.studentprofile.phone, sms_message)
        sms_client.send_message(parent.phone, sms_message)
