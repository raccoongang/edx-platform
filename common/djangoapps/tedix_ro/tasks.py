from collections import defaultdict
from datetime import datetime, timedelta
from urlparse import urljoin

from babel.dates import format_datetime
from celery.schedules import crontab
from celery.task import periodic_task, task
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import ugettext as _
import pytz

from edxmako.shortcuts import render_to_string
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from .models import StudentCourseDueDate, StudentReportSending, StudentCourseReport, StudentProfile, Classroom
from .sms_client import SMSClient
from .utils import create_student_course_report

TEACHER_EXTENDED_REPORT_TIME_RANGE = 1 # in minutes


@periodic_task(run_every=crontab(minute='*/{}'.format(TEACHER_EXTENDED_REPORT_TIME_RANGE)))
def send_teacher_extended_reports():
    """
    Sends extended report for the teacher with all his courses and all his students
    """
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    course_due_dates = StudentCourseDueDate.objects.filter(
        due_date__range=(datetime_now - timedelta(minutes=TEACHER_EXTENDED_REPORT_TIME_RANGE), datetime_now),
        creator__instructorprofile__user__is_staff=True
    ).values(
        'course_id', 'student__user_id', 'creator_id', 'id'
    ).distinct()
    grouped_due_dates = defaultdict(dict)
    for course_due_date in course_due_dates:
        creator_id = course_due_date['creator_id']
        if 'courses' not in grouped_due_dates[creator_id]:
            grouped_due_dates[creator_id] = {
                'courses': defaultdict(list)
            }
        grouped_due_dates[creator_id]['courses'][course_due_date['course_id']].append((
            course_due_date['student__user_id'],
            course_due_date['id']
        ))

    for creator_id in grouped_due_dates:
        instructor_user = User.objects.get(id=creator_id)
        lesson_reports = []
        for course_id in grouped_due_dates[creator_id]['courses']:
            report_data = []
            header = []
            for student_user_id, due_date_id in grouped_due_dates[creator_id]['courses'][course_id]:
                student_course_report = StudentCourseReport.objects.filter(
                    student__user_id=student_user_id,
                    course_id=course_id,
                    course_due_date_id=due_date_id
                ).first()
                if not student_course_report:
                    student_course_report = create_student_course_report(student_user_id, course_id, due_date_id)
                header, user_data = student_course_report.data.values()
                report_data.append(user_data)
            if report_data:
                lesson_reports.append({
                    'course_name': student_course_report.course.display_name,
                    'header': header,
                    'report_data': report_data,
                    'report_url': urljoin(
                        configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                        reverse('extended_report', kwargs={'course_key': student_course_report.course.id})
                    )
                })
        if lesson_reports:
            subject = _(u'{platform_name}: Report for {username}').format(
                platform_name=settings.PLATFORM_NAME,
                username=instructor_user.profile.name or instructor_user.username
            )
            context = {
                'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                'user': instructor_user,
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
            send_mail(subject, txt_message, from_address, [instructor_user.email], html_message=html_message)


@periodic_task(run_every=crontab(hour='15', minute='30'))
def send_extended_reports_by_deadline():
    """
    Sends an extended report to the student if the course deadline has expired in the last 24 hours
    and the course report has not been sended
    """
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    for due_date in StudentCourseDueDate.objects.filter(
            due_date__lte=datetime_now,
            due_date__gt=datetime_now-timedelta(1)):
        user = due_date.student.user
        course_id = due_date.course_id
        student_report_sending_exists = StudentReportSending.objects.filter(
            course_id=course_id,
            user=user
        ).exists()
        if not student_report_sending_exists:
            course_report = due_date.course_reports.filter(student__user=user).first()
            if not course_report:
                course_report = create_student_course_report(user.id, course_id, due_date.id)
            send_student_extended_reports(course_report.id)
            StudentReportSending.objects.create(
                course_id=course_id,
                user=user,
            )



@task
def send_student_completed_report(course_report_id):
    """
    Sends an extended report to the student if StudentCourseReport has been generated and
    student has due date for course
    """
    course_report = StudentCourseReport.objects.filter(id=course_report_id).first()
    course_completed = course_report and course_report.data['report_data']['completion']
    if course_completed:
        user = course_report.student.user
        course_id=course_report.course_id
        student_report_sending_exists = StudentReportSending.objects.filter(
            course_id=course_id,
            user=user
        ).exists()
        if not student_report_sending_exists and course_report.course_due_date:
            send_student_extended_reports(course_report_id)
            StudentReportSending.objects.create(
                course_id=course_id,
                user=user,
            )


@task
def send_student_extended_reports(course_report_id):
    """
    Sends email and SMS with an extended report for student and his parent
    """
    student_course_report = StudentCourseReport.objects.filter(id=course_report_id).first()
    if student_course_report:
        user = student_course_report.student.user
        course_key=student_course_report.course_id
        user_data = student_course_report.data.get('report_data')
        course = student_course_report.course
        lesson_reports = [{
                'course_name': course.display_name,
                'report_data': [user_data,],
                'report_url': urljoin(
                    configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                    reverse('extended_report', kwargs={'course_key': course.id, 'course_report_id': student_course_report.id})
                )
            }]
        subject = _(u'{platform_name}: Report for {username} on "{course_name}"').format(
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
        mail_recipients = [user.email,]

        parent = user.studentprofile.parents.first()
        if parent and parent.user.email:
            mail_recipients.append(parent.user.email)

        send_mail(subject, txt_message, from_address, mail_recipients, html_message=html_message)

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
        if parent and parent.phone:
            sms_client.send_message(parent.phone, sms_message)


@periodic_task(run_every=crontab(0, 0, day_of_month='1', month_of_year='9'))
def move_students_to_higher_classroom():
    """
    Assigns all students to the higher classroom that were registered more than month ago
    """
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    august_1st = datetime(datetime_now.year, 8, 1).replace(tzinfo=pytz.UTC)
    students = StudentProfile.objects.exclude(Q(user__date_joined__gte=august_1st) | Q(classroom__name__startswith='8'))
    for student in students:
        current_classroom = getattr(student.classroom, 'name', None)

        next_classroom_number = None
        if current_classroom and current_classroom[0].isdigit():
            next_classroom_number = int(current_classroom[0]) + 1

        if next_classroom_number:
            next_classroom_name = '{}{}'.format(next_classroom_number, current_classroom[1:])
            classroom, created = Classroom.objects.get_or_create(name=next_classroom_name)
            student.classroom = classroom
            student.save()
