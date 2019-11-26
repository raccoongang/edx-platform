import datetime
import json
import pytz
from csv import DictReader
from urlparse import urljoin

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View

from courseware.access import has_access
from courseware.courses import get_course_with_access, get_studio_url
from courseware.masquerade import setup_masquerade
from edxmako.shortcuts import render_to_response
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.permissions import CanRetireUser
from openedx.core.djangoapps.user_api.accounts.utils import generate_password
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
import pytz
from student.helpers import do_create_account, get_next_url_for_login_page
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore

from .admin import INSTRUCTOR_EXPORT_FIELD_NAMES, STUDENT_PARENT_EXPORT_FIELD_NAMES
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
from .models import City, School, StudentCourseDueDate, StudentProfile, VideoLesson
from .serializers import (
    CitySerializer,
    SchoolSerilizer,
    SingleCitySerializer,
    SingleSchoolSerilizer,
    VideoLessonSerializer,
)
from .utils import get_payment_link, report_data_preparation, light_report_data_preparation


def extended_report(request, course_key):
    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    course_key = CourseKey.from_string(course_key)
    course = get_course_with_access(user, 'load', course_key, check_if_enrolled=True)

    report_data = []
    modulestore_course = modulestore().get_course(course_key)
    if user.is_superuser:
        for student in User.objects.filter(courseenrollment__course_id=course.id, is_staff=False).select_related('profile'):
            header, user_data = report_data_preparation(student, modulestore_course)
            report_data.append(user_data)
    elif user.is_staff and hasattr(user, 'instructorprofile'):
        for student_profile in user.instructorprofile.students.filter(
            user__courseenrollment__course_id=course.id
        ).select_related('user__profile'):
            header, user_data = report_data_preparation(student_profile.user, modulestore_course)
            report_data.append(user_data)
    else:
        header, user_data = report_data_preparation(user, modulestore_course)
        report_data.append(user_data)
    context = {
        'course_name': course.display_name,
        'header': header,
        'report_data': report_data,
        'user': user,
    }
    return render_to_response('extended_report.html', context)



def manage_courses(request):
    InstructorProfile = apps.get_model('tedix_ro', 'InstructorProfile')
    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    if not (user.is_staff or user.is_superuser):
        return redirect(reverse('dashboard'))

    context = {
        "csrftoken": csrf(request)["csrf_token"],
        'show_dashboard_tabs': True
    }
    try:
        if user.is_superuser:
            students = StudentProfile.objects.filter(user__is_active=True)
        else:
            students = user.instructorprofile.students.filter(user__is_active=True)
    except InstructorProfile.DoesNotExist:
        students = StudentProfile.objects.none()

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    courses = CourseOverview.objects.filter(enrollment_end__gt=now, enrollment_start__lt=now)
    form = StudentEnrollForm(students=students, courses=courses)
    if request.method == 'POST':
        data = dict(
            courses = map(CourseKey.from_string, request.POST.getlist('courses')),
            students = request.POST.getlist('students'),
            due_date = request.POST.get('due_date'),
            send_to_students=request.POST.get('send_to_students'),
            send_to_parents=request.POST.get('send_to_parents'),
            send_sms=request.POST.get('send_sms')
        )
        form = StudentEnrollForm(data=data, courses=courses, students=students)
        if form.is_valid():
            for student in form.cleaned_data['students']:
                courses_list = []
                for course in form.cleaned_data['courses']:
                    due_date = form.cleaned_data['due_date']
                    CourseEnrollment.enroll_by_email(student.user.email, course.id)
                    StudentCourseDueDate.objects.update_or_create(
                        student=student,
                        course_id=course.id,
                        defaults={'due_date':form.cleaned_data['due_date']}
                    )
                    courses_list.append([
                        urljoin(settings.LMS_ROOT_URL, reverse('openedx.course_experience.course_home', kwargs={'course_id': course.id})),
                        course.display_name
                    ])
                    user_time_zone = student.user.preferences.filter(key='time_zone').first()
                    if user_time_zone:
                        user_tz = pytz.timezone(user_time_zone.value)
                        course_tz_due_datetime = pytz.UTC.localize(due_date.replace(tzinfo=None), is_dst=None).astimezone(user_tz)
                        context = {
                            'courses': courses_list,
                            'due_date': course_tz_due_datetime.strftime(
                                "%b %d, %Y, %H:%M %P {} (%Z, UTC%z)".format(user_time_zone.value.replace("_", " "))
                            )
                        }
                    else:
                        context = {
                            'courses': courses_list,
                            'due_date': '{} UTC'.format(due_date.astimezone(pytz.UTC).strftime('%b %d, %Y, %H:%M %P'))
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
                    # sending sms logic to be here
                    pass
            messages.success(request, 'Successfully assigned.')
            return redirect(reverse('manage_courses'))

    context.update({
        'form': form
    })

    return render_to_response('manage_courses.html', context)


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
            'site_header': 'LMS Administration',
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
                        form_data = {FORM_FIELDS_MAP.get(k, k):v for k,v in row.items()}
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
            'site_header': 'LMS Administration',
            'row_headers': self.headers
        })
        return render(request, self.template_name, context)

    def send_email(self, user, data, send_payment_link=False):
        to_address = user.email
        status = 'Elev' if self.role == 'student' else 'Profesor'
        email_context = {
            'status': status,
            'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
            'support_url': configuration_helpers.get_value('SUPPORT_SITE_LINK', settings.SUPPORT_SITE_LINK),
            'support_email': configuration_helpers.get_value('CONTACT_EMAIL', settings.CONTACT_EMAIL),
            'email': to_address,
            'password': data['password']
        }
        subject = 'Bine ati venit pe platforma {}'.format(
            configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
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
    headers = INSTRUCTOR_EXPORT_FIELD_NAMES
    profile_form = InstructorImportValidationForm
    template_name = 'admin_import.html'
    role = 'instructor'
    changelist_url = reverse_lazy('admin:tedix_ro_instructorprofile_changelist')
    text_changelist_url = 'Instructor_profiles'


class StudentProfileImportView(ProfileImportView):
    import_form = StudentProfileImportForm
    headers = STUDENT_PARENT_EXPORT_FIELD_NAMES
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
