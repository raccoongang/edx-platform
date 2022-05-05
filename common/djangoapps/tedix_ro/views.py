import datetime
import json
import time
from csv import DictReader
from urlparse import urljoin

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, ugettext as _
from django.views import View

from courseware.courses import get_course_with_access
from edxmako.shortcuts import render_to_response, render_to_string as mako_render_to_string
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangolib.translation_utils import translate_date
import pytz
from student.helpers import do_create_account, get_next_url_for_login_page
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore

from .admin import INSTRUCTOR_IMPORT_FIELD_NAMES, STUDENT_PARENT_IMPORT_FIELD_NAMES, EMPTY_VALUE
from .forms import (
    FORM_FIELDS_MAP,
    AccountImportValidationForm,
    CityImportForm,
    CityImportValidationForm,
    InstructorImportValidationForm,
    ProfileImportForm,
    SchoolImportValidationForm,
    StudentEnrollForm,
    StudentImportRegisterForm,
    StudentProfileImportForm,
)
from .models import (
    City,
    School,
    StudentCourseDueDate,
    StudentProfile,
    VideoLesson,
    Classroom,
    StudentReportSending,
    StudentCourseReport,
    )
from .serializers import (
    CitySerializer,
    SchoolSerilizer,
    SingleCitySerializer,
    SingleSchoolSerilizer,
    VideoLessonSerializer,
)
from .sms_client import SMSClient
from .tasks import send_student_completed_report
from .utils import (
    get_payment_link,
    reset_student_progress,
    get_user_time_zone,
    get_timezoned_date,
    create_student_course_report
)


def my_reports(request):
    """
    Provides a list of available homework assignments, for the student/parent/teacher/superuser.
    """
    def user_due_date_data(user, due_date):
        """
        Function returns updated course due date data depends on user timezone if he has it.
        Arguments:
            user: instance of model User.
            due_date: datetime/date field when Course Enrollment model was created.
        Returns: 
            dict: {
                "date_group": today/tomorrow/future/past,
                "date_data": 2020-06-01,
                "displayed_date" Today/Tomorrow/Future: 1 Jun/ Past: 1 Jun,
            }
        """
        due_date_data = {}
        date_group = ''
        utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        user_time_zone = user.preferences.filter(key='time_zone').first()
        language = get_language()

        if isinstance(due_date, datetime.datetime):
            date_utc = due_date.replace(tzinfo=None)
            if user_time_zone:
                user_tz = pytz.timezone(user_time_zone.value)
                date = pytz.UTC.localize(due_date.replace(tzinfo=None), is_dst=None).astimezone(user_tz)
            else:
                date = due_date.astimezone(pytz.UTC)
            due_date = due_date.date()
        else:
            date = due_date

        today = utc_now.date()
        date_data = time.mktime(date_utc.timetuple())
        _today = _('Today')
        _tomorrow = _('Tomorrow')
        _future = _('Future')
        _past = _('Past')
        date_group_css_map = {
            _today: 'today',
            _tomorrow: 'tomorrow',
            _future: 'future',
            _past: 'past'
        }
        if today == due_date:
            date_group = _today
            due_date_data.update({
                'displayed_date': date_group,
                'due_date_order': 1
            })
        elif (today - due_date).days == -1:
            date_group = _tomorrow
            due_date_data.update({
                'displayed_date': date_group,
                'due_date_order': 2
            })
        elif (today - due_date).days < -1:
            date_group = _future
            due_date_data.update({
                'displayed_date': '{}: {}'.format(date_group, translate_date(date, language)),
                'due_date_order': 3
            })
        elif (today - due_date).days > 0:
            date_group = _past
            due_date_data.update({
                'displayed_date': '{}: {}'.format(date_group, translate_date(date, language)),
                'due_date_order': 4
            })
            date_data *= -1

        due_date_data.update({
            'date_group': date_group_css_map[date_group],
            'date_data': date_data,
        })
        return due_date_data

    user = request.user

    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    data = []
    utc_now_date = datetime.datetime.utcnow().date()

    if hasattr(user, 'studentprofile'): 
        student = user.studentprofile
        student_class = student.classroom
        student_course_reports = StudentCourseReport.objects.filter(
            student=student,
        )
        for course_report in student_course_reports:
            course_key = course_report.course_id
            course_due_date = course_report.course_due_date
            course_report_link = reverse('extended_report', kwargs={'course_key': unicode(course_key), 'course_report_id': course_report.id})
            earned = course_report.data['report_data']['earned']
            possible = course_report.data['report_data']['possible']
            complete = course_report.data['report_data']['completion']
            average_score = 'n/a'

            default_course_due_date_data = {
                'due_date_order': 5,
                'date_group': '',
                'date_data': '',
                'displayed_date': 'n/a',
            }
            course_due_date_data = user_due_date_data(user, course_due_date.due_date) if course_due_date else default_course_due_date_data

            if earned:
                average_score = '{:.2f}'.format(
                    float(earned) / possible * 10
                )

            finalize_date_timezoned = get_timezoned_date(student.user, course_report.created_time)

            data.append({
                'complete': complete,
                'course_name': course_report.course.display_name,
                'report_link': course_report_link,
                'due_date': course_due_date_data,
                'classroom': student_class,
                'average_score': average_score,
                'has_due_date': _('Yes') if course_due_date else _('No'),
                'finalize_date': {
                    'display_data': finalize_date_timezoned.strftime("%b %d, %Y, %H:%M %P UTC%z"),
                    'date_data': time.mktime(course_report.created_time.timetuple()),
                },
                'active_report_link': True,
            })
    else:
        if user.is_superuser:
            students_classes = user.course_due_dates.values_list('student__classroom__name', flat=True).distinct()
        elif hasattr(user, 'instructorprofile'):
            students_classes = user.instructorprofile.students.all().values_list('classroom__name', flat=True).distinct()

        course_ids = user.course_due_dates.values_list('course_id', flat=True).distinct()
        for course_id in course_ids:
            course = CourseOverview.get_from_id(course_id)
            course_report_link = reverse('extended_report', kwargs={'course_key': unicode(course_id)} )
            for students_class in students_classes:
                course_due_dates_past = user.course_due_dates.filter(
                    due_date__lt=utc_now_date,
                    student__classroom__name=students_class,
                    course_id=course_id,
                ).order_by('-due_date').values_list('due_date', flat=True)[:200]

                course_due_dates = user.course_due_dates.filter(
                    due_date__gte=utc_now_date,
                    student__classroom__name=students_class,
                    course_id=course_id,
                ).values_list('due_date', flat=True).union(course_due_dates_past).distinct()

                for course_due_date in course_due_dates:
                    students_in_class = user.course_due_dates.filter(
                        due_date=course_due_date,
                        student__classroom__name=students_class,
                        course_id=course_id,
                    ).values_list('student__user_id', flat=True).distinct()

                    possible = earned = 0
                    has_students_with_report = False
                    course_reports = StudentCourseReport.objects.filter(
                        student__user_id__in=students_in_class,
                        course_id=course_id,
                        course_due_date__due_date=course_due_date
                    )
                    for course_report in course_reports:
                        course_report_data = course_report.data
                        has_students_with_report = True
                        earned += course_report_data['report_data']['earned']
                        possible += course_report_data['report_data']['possible']

                    average_score = 0
                    if earned:
                        average_score = (float(earned) / possible) * 10

                    data.append({
                        'course_name': course.display_name,
                        'active_report_link': has_students_with_report,
                        'report_link': course_report_link,
                        'due_date': user_due_date_data(user, course_due_date),
                        'classroom': students_class,
                        'average_score': round(average_score, 2) if average_score else 'n/a',
                    })

    context = {
        'data': data,
    }

    if request.is_ajax():
        html = mako_render_to_string('my_reports.html', context)
        return HttpResponse(json.dumps({'html': html}), content_type="application/json")
    return render_to_response('my_reports.html', context)


def my_reports_main(request):
    if not request.user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    return render_to_response('my_reports_main.html')


@api_view(['GET'])
def create_report(request, course_key):
    user = request.user
    if not user.is_authenticated():
        raise Http404
    course_key = CourseKey.from_string(course_key)

    report_data = []
    course = get_course_with_access(user, 'load', course_key, check_if_enrolled=True)
    student_course_report = create_student_course_report(user.id, course_key)
    send_student_completed_report.apply_async(args=(student_course_report.id, ), countdown=5)
    header, user_data = student_course_report.data.values()
    report_data.append(user_data)
    context = {
        'course_name': course.display_name,
        'header': header,
        'report_data': report_data,
        'user': user,
    }

    reset_student_progress(user, course_key)
    if request.is_ajax():
        course_due_date = student_course_report.course_due_date
        today = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).date()
        due_date_value = 'n/a'
        if course_due_date:
            due_date = course_due_date.due_date.date()
            if today == due_date:
                date_group = _('Today')
            elif (today - due_date).days == -1:
                date_group = _('Tomorrow')
            elif (today - due_date).days < -1:
                date_group = _('Future')
            elif (today - due_date).days > 0:
                date_group = _('Past')
            due_date_value = '{}, {}'.format(date_group.encode('utf8'), translate_date(due_date, get_language()))

        context.update({
            'due_date': due_date_value,
        })
        html = mako_render_to_string('extended_report_popup.html', context)
        return Response({'html': html})
    return render_to_response('extended_report.html', student_course_report.data)


def extended_report(request, course_key, course_report_id=None):
    """
    Provides an extended report, depending on the role
    """
    classroom = request.GET.get('classroom')
    due_date_str = request.GET.get('due_date')
    due_date = None
    if due_date_str:
        due_date = pytz.UTC.localize(datetime.datetime.fromtimestamp(float(due_date_str).__abs__()))

    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    course_key = CourseKey.from_string(course_key)
    course = get_course_with_access(user, 'load', course_key, check_if_enrolled=True)
    header = []
    report_data = []
    query_params = {}
    
    def add_report(students):
        header = []
        for student in students:
            student_course_report = StudentCourseReport.objects.filter(
                student__user=student if isinstance(student, User) else student.user,
                course_id=course_key,
            )
            if due_date:
                student_course_report = student_course_report.filter(course_due_date__due_date=due_date)
            student_course_report = student_course_report.first()

            if student_course_report:
                header, user_data = student_course_report.data.values()
                report_data.append(user_data)
        # header is always the same
        return header
    
    def get_users_from_due_dates(classroom, due_date):
        if classroom:
            query_params['student__classroom__name'] = classroom
        if due_date:
            query_params['due_date'] = due_date # TODO: consider using __year, __month, __day lookups

        return StudentCourseDueDate.objects.filter(course_id=course_key, **query_params).values_list('student__user_id').distinct()

    if user.is_superuser:
        students = User.objects.filter(id__in=get_users_from_due_dates(classroom, due_date))
        header = add_report(students)

    elif user.is_staff and hasattr(user, 'instructorprofile'):
        students = user.instructorprofile.students.filter(
            user__courseenrollment__course_id=course.id,
            user_id__in=get_users_from_due_dates(classroom, due_date)
        ).select_related('user__profile').distinct()
        header = add_report(students)

    else:
        student_course_report = get_object_or_404(StudentCourseReport, id=course_report_id, course_id=course_key, student__user=user)
        header, user_data = student_course_report.data.values()
        report_data.append(user_data)

    if not report_data:
        raise Http404

    context = {
        'course_name': course.display_name,
        'header': header,
        'report_data': report_data,
        'user': user,
        'classroom': classroom,
        'due_date': 'n/a',
    }
    if request.is_ajax():
        if due_date:
            today = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).date()
            due_date_date = due_date.date()
            if today == due_date_date:
                date_group = _('Today')
            elif (today - due_date_date).days == -1:
                date_group = _('Tomorrow')
            elif (today - due_date_date).days < -1:
                date_group = _('Future')
            elif (today - due_date_date).days > 0:
                date_group = _('Past')
            context.update({
                'due_date': '{}, {}'.format(date_group.encode('utf8'), translate_date(due_date, get_language())),
            })

        html = mako_render_to_string('extended_report_popup.html', context)
        return HttpResponse(json.dumps({'html': html}), content_type="application/json")
    else:
        return render_to_response('extended_report.html', context)


def manage_courses(request):
    InstructorProfile = apps.get_model('tedix_ro', 'InstructorProfile')
    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    if not (user.is_staff or user.is_superuser):
        return redirect(reverse('dashboard'))

    user_tz = get_user_time_zone(user)
    user_timezone_str = datetime.datetime.now(user_tz).strftime('UTC%z')
    context = {
        'csrftoken': csrf(request)['csrf_token'],
        'show_dashboard_tabs': True,
        'timezone': user_timezone_str
    }
    try:
        if user.is_superuser:
            students = StudentProfile.objects.filter(user__is_active=True)
        else:
            students = user.instructorprofile.students.filter(user__is_active=True)
    except InstructorProfile.DoesNotExist:
        students = StudentProfile.objects.none()

    classrooms = Classroom.objects.all()
    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    courses = CourseOverview.objects.filter(enrollment_end__gt=utc_now, enrollment_start__lt=utc_now)
    form = StudentEnrollForm(students=students, courses=courses, classrooms=classrooms, user_tz=user_tz)
    if request.method == 'POST':
        data = dict(
            courses = map(CourseKey.from_string, request.POST.getlist('courses')),
            students = request.POST.getlist('students'),
            due_date = request.POST.get('due_date'),
            send_to_students=request.POST.get('send_to_students'),
            send_to_parents=request.POST.get('send_to_parents'),
            send_sms=request.POST.get('send_sms')
        )
        form = StudentEnrollForm(data=data, courses=courses, students=students, classrooms=classrooms, user_tz=user_tz)
        if form.is_valid():
            sms_client = SMSClient()
            for student in form.cleaned_data['students']:
                courses_list = []
                for course in form.cleaned_data['courses']:
                    due_date = form.cleaned_data['due_date']
                    CourseEnrollment.enroll_by_email(student.user.email, course.id)
                    reset_student_progress(student.user, course.id)
                    StudentReportSending.objects.filter(course_id=course.id, user=student.user).delete()
                    course_due_date = StudentCourseDueDate.objects.filter(
                        student=student,
                        course_id=course.id,
                        due_date__gt=utc_now
                    )
                    if course_due_date:
                        course_due_date.update(
                            creator=user,
                            due_date=due_date
                        )
                    else:
                        StudentCourseDueDate.objects.create(
                            student=student,
                            course_id=course.id,
                            creator=user,
                            due_date=due_date
                        )
                    courses_list.append([
                        urljoin(settings.LMS_ROOT_URL,
                        reverse(
                            'jump_to',
                            kwargs={
                                'course_id': course.id,
                                'location': modulestore().make_course_usage_key(course.id)
                            }
                        )),
                        course.display_name
                    ])
                    course_tz_due_datetime = get_timezoned_date(student.user, due_date)
                    context = {
                        'courses': courses_list,
                        'due_date': course_tz_due_datetime.strftime("%b %d, %Y, %H:%M %P (%Z, UTC%z)")
                    }

                context.update({
                    'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
                    'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
                    'support_url': configuration_helpers.get_value('SUPPORT_SITE_LINK', settings.SUPPORT_SITE_LINK),
                    'support_email': configuration_helpers.get_value('CONTACT_EMAIL', settings.CONTACT_EMAIL)
                })
                from_address = configuration_helpers.get_value(
                    'email_from_address',
                    settings.DEFAULT_FROM_EMAIL
                )
                subject = u"{} - Tema de casa - Data limita: {}".format(
                    configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
                    due_date.astimezone(pytz.UTC).strftime('%d %b %Y')
                )
                if form.cleaned_data['send_to_students']:
                    html_message = render_to_string(
                        'emails/student_enroll_email_message.html',
                        context
                    )
                    txt_message = render_to_string(
                        'emails/student_enroll_email_message.txt',
                        context
                    )
                    send_mail(subject, txt_message, from_address, [student.user.email], html_message=html_message)
                if form.cleaned_data['send_to_parents']:
                    parent = student.parents.first()
                    if parent and parent.user:
                        html_message = render_to_string(
                            'emails/parent_enroll_email_message.html',
                            context
                        )
                        txt_message = render_to_string(
                            'emails/parent_enroll_email_message.txt',
                            context
                        )
                        send_mail(subject, txt_message, from_address, [parent.user.email], html_message=html_message)

                if form.cleaned_data['send_sms']:
                    parent = student.parents.first()
                    context.update({
                        'student_name': student.user.profile.name or student.user.username,
                        'courses_due_dates_url': urljoin(settings.LMS_ROOT_URL, reverse('personal_due_dates')),
                    })
                    sms_message = render_to_string(
                        'sms/manage_course_notify.txt',
                        context
                    )
                    sms_client.send_message(parent.phone, sms_message)
            messages.success(request, _('Successfully assigned.'))
            if request.is_ajax():
                html = mako_render_to_string('manage_courses.html', {
                    "csrftoken": csrf(request)["csrf_token"],
                    'show_dashboard_tabs': True,
                    'form': StudentEnrollForm(courses=courses, students=students, classrooms=classrooms, user_tz=user_tz),
                    'timezone': user_timezone_str
                })
                return HttpResponse(json.dumps({'html': html}), content_type="application/json")
            return redirect(reverse('manage_courses'))
    context.update({
        'form': form
    })
    if request.is_ajax():
        html = mako_render_to_string('manage_courses.html', context)
        return HttpResponse(json.dumps({'html': html}), content_type="application/json")

    return render_to_response('manage_courses.html', context)


def manage_courses_main(request):
    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    if not (user.is_staff or user.is_superuser):
        return redirect(reverse('dashboard'))
    return render_to_response('manage_courses_main.html')


def personal_due_dates(request):
    """
    Render student's personal due dates for courses with an active enrollment.
    """

    def format_due_date(student_profile, due_date):
        """
        Format due_date based on user preferences.
        """
        language = get_language()
        course_tz_due_datetime = get_timezoned_date(student_profile.user, due_date)
        return  '{}, {}'.format(
            translate_date(course_tz_due_datetime, language),
            course_tz_due_datetime.strftime("%H:%M %P (%Z, UTC%z)")
        )

    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    context = {'show_dashboard_tabs': True}
    try:
        student = StudentProfile.objects.get(user=user)
    except (StudentProfile.DoesNotExist, StudentProfile.MultipleObjectsReturned):
        return redirect(reverse('dashboard'))

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    course_ids = CourseOverview.objects.filter(
        enrollment_end__gt=now,
        enrollment_start__lt=now
    ).values_list('id', flat=True)

    student_due_dates = StudentCourseDueDate.objects.filter(
        student=student,
        course_id__in=course_ids,
        due_date__gt=now
    ).order_by('-due_date')

    courses_due_dates_list = [
        [
            urljoin(
                settings.LMS_ROOT_URL,
                reverse(
                    'jump_to',
                    kwargs={
                        'course_id': unicode(student_due_date.course_id),
                        'location': modulestore().make_course_usage_key(student_due_date.course_id)
                    }
                )
            ),
            CourseOverview.objects.get(id=student_due_date.course_id).display_name,
            format_due_date(student, student_due_date.due_date)
        ] for student_due_date in student_due_dates
    ]

    context.update({
        'courses_due_dates': courses_due_dates_list,
    })

    return render_to_response('personal_due_dates.html', context)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    paginator = None
    pagination_class = None

    def get_serializer_class(self):
        if self.kwargs.get('pk'):
            return CitySerializer
        return SingleSchoolSerilizer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    paginator = None
    pagination_class = None

    def get_serializer_class(self):
        if self.kwargs.get('pk'):
            return SchoolSerilizer
        return SingleCitySerializer


class VideoLessonViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VideoLessonSerializer
    queryset = VideoLesson.objects.all()
    paginator = None
    pagination_class = None

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileImportView(View):
    import_form = ProfileImportForm
    headers = []
    profile_form = None
    template_name = None
    role = None
    text_changelist_url = None
    changelist_url = None

    def get(self, request, *args, **kwargs):
        context = {
            'text_changelist_url': self.text_changelist_url,
            'changelist_url': self.changelist_url,
            'import_form': self.import_form,
            'site_header': _('LMS Administration'),
            'row_headers': self.headers
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data_list = []
        import_form = self.import_form(request.POST, request.FILES)
        context = {'data_list': data_list}
        if import_form.is_valid():
            with transaction.atomic():
                try:
                    if import_form.cleaned_data['file_format'] == 'csv':
                        dataset = DictReader(import_form.cleaned_data['file_to_import'])
                    if import_form.cleaned_data['file_format'] == 'json':
                        dataset = json.loads(import_form.cleaned_data['file_to_import'].read())
                    for i, row in enumerate(dataset, 1):
                        errors = {}
                        form_data = self.replace_empty_value(row)
                        form_data['role'] = self.role
                        form_data['password'] = User.objects.make_random_password()
                        user_form = AccountImportValidationForm(form_data, tos_required=False)
                        profile_form = self.profile_form(form_data)
                        state = 'new'
                        if user_form.is_valid() and profile_form.is_valid():
                            if profile_form.exists(form_data):
                                state = profile_form.update(form_data)
                            else:
                                user, profile, registration = do_create_account(user_form, profile_form)
                                registration.activate()
                                if self.role == 'instructor':
                                    user.is_staff = True
                                    user.save()
                                    self.send_email(user, form_data)
                                elif self.role == 'student':
                                    self.send_email(user, form_data, import_form.cleaned_data['send_payment_link'])
                        else:
                            state = 'error'
                            errors.update(dict(user_form.errors.items()))
                            errors.update(dict(profile_form.errors.items()))
                        data_list.append((i, errors, state, row))
                except Exception:
                    messages.error(request, 'Oops! Something went wrong. Please check that the file structure is correct.')
                    context.pop('data_list')
                    transaction.set_rollback(True)
        context.update({
            'text_changelist_url': self.text_changelist_url,
            'changelist_url': self.changelist_url,
            'import_form': import_form,
            'site_header': _('LMS Administration'),
            'row_headers': self.headers
        })
        return render(request, self.template_name, context)

    def replace_empty_value(self, row):
        form_data = {}
        for key, value in row.items():
            if value == EMPTY_VALUE:
                value = ''
            form_data.update({FORM_FIELDS_MAP.get(key, key): value})
        return form_data

    def send_email(self, user, data, send_payment_link=False):
        to_address = user.email
        status = _('Elev') if self.role == 'student' else _('Profesor')
        email_context = {
            'status': status,
            'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
            'support_url': configuration_helpers.get_value('SUPPORT_SITE_LINK', settings.SUPPORT_SITE_LINK),
            'support_email': configuration_helpers.get_value('CONTACT_EMAIL', settings.CONTACT_EMAIL),
            'email': to_address,
            'password': data['password']
        }
        subject = _('Bine ati venit pe platforma {platform_name}').format(
            platform_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
        )
        from_address = configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL)
        message = render_to_string('emails/import_profile.txt', email_context)
        send_mail(subject, message, from_address, [to_address])
        if self.role == 'student':
            parent_user = user.studentprofile.parents.first()
            if parent_user and parent_user.user and not parent_user.user.has_usable_password():
                password = User.objects.make_random_password()
                parent_user.user.set_password(password)
                parent_user.user.save()
                email_context.update({
                    'status': 'Parinte',
                    'email': parent_user.user.email,
                    'password': password
                })
                message = render_to_string('emails/import_profile.txt', email_context)
                send_mail(subject, message, from_address, [parent_user.user.email])
                if send_payment_link:
                    email_context.update({
                        'payment_link': get_payment_link(parent_user.user),
                    })
                    message = render_to_string('emails/payment_link_email_parent.txt', email_context)
                    subject = 'Plata abonament {}'.format(
                        configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
                    )
                    send_mail(subject, message, from_address, [parent_user.user.email])


class InstructorProfileImportView(ProfileImportView):
    import_form = ProfileImportForm
    headers = INSTRUCTOR_IMPORT_FIELD_NAMES
    profile_form = InstructorImportValidationForm
    template_name = 'admin_import.html'
    role = 'instructor'
    changelist_url = reverse_lazy('admin:tedix_ro_instructorprofile_changelist')
    text_changelist_url = 'Instructor_profiles'


class StudentProfileImportView(ProfileImportView):
    import_form = StudentProfileImportForm
    headers = STUDENT_PARENT_IMPORT_FIELD_NAMES
    profile_form = StudentImportRegisterForm
    template_name = 'admin_import.html'
    role = 'student'
    changelist_url = reverse_lazy('admin:tedix_ro_studentprofile_changelist')
    text_changelist_url = 'Student profiles'


def city_import(request):
    headers = ['city_name', 'school_name', 'school_type']
    import_form = CityImportForm()
    context = {
        'import_form': import_form,
        'text_changelist_url': 'Cities',
        'changelist_url': reverse_lazy('admin:tedix_ro_city_changelist'),
        'site_header': 'LMS Administration',
        'row_headers': headers
    }
    status_map = {
        'Publica': 'Public',
        'Privata': 'Private'
    }
    if request.method == 'POST':
        import_form = CityImportForm(request.POST, request.FILES)
        if import_form.is_valid():
            dataset = json.loads(import_form.cleaned_data['file_to_import'].read())
            data_list = []
            context.update({'data_list': data_list})
            with transaction.atomic():
                try:
                    for city_name, schools in dataset.items():
                        errors = {}
                        status = ''
                        city_form = CityImportValidationForm({"name": city_name})
                        if city_form.is_valid():
                            if not city_form.exists(city_name):
                                city_form.save()
                                state = 'new'
                            else:
                                state = 'skipped'
                            for school_name, status in [(school, status) for x in schools for (school, status) in x.items()]:
                                errors = {}
                                school_type = status_map.get(status, '')
                                school_form = SchoolImportValidationForm({
                                    'name': school_name,
                                    'city': city_name,
                                    'school_type': school_type
                                })

                                if school_form.is_valid():
                                    if school_form.exists(school_name, city_name):
                                        state = school_form.update(school_name, city_name, school_type)
                                    else:
                                        school_form.save()
                                        state = 'new'
                                else:
                                    errors.update(dict(school_form.errors.items()))
                                    state = 'error'
                                
                                data_list.append((errors, state, {
                                    'city_name': city_name,
                                    'school_name': school_name,
                                    'school_type': status
                                }))
                            if not next(iter(schools), None):
                                data_list.append((errors, state, {
                                    'city_name': city_name,
                                    'school_name': '',
                                    'school_type': status
                                }))
                        else:
                            for value in city_form.errors.values():
                                errors.update({'city': value})
                            state = 'error'
                            data_list.append((errors, state, {
                                'city_name': city_name
                            }))

                except Exception:
                    messages.error(request, u'Oops! Something went wrong. Please check that the file structure is correct.')
                    context.pop('data_list')
                    transaction.set_rollback(True)
        context.update({'import_form': import_form})
    return render(request, 'city_import.html', context)

def email_verification(request):
    return render_to_response('email_verification.html')
