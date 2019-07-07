import datetime
from collections import OrderedDict
import pytz
import tablib
from urlparse import urljoin

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from rest_framework import generics, viewsets

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from student.models import CourseEnrollment
from student.helpers import get_next_url_for_login_page, do_create_account

from .admin import STUDENT_PARENT_EXPORT_FIELD_NAMES
from .forms import StudentEnrollForm, StudentImportForm, AccountImportValidationForm, StudentImportRegisterForm
from .models import StudentProfile, StudentCourseDueDate, City, School
from .serializers import CitySerializer, SchoolSerilizer, SingleCitySerializer, SingleSchoolSerilizer


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
                html_message = render_to_string(
                    'emails/student_enroll_email_message.html',
                    context
                )
                txt_message = render_to_string(
                    'emails/student_enroll_email_message.txt',
                    context
                )
                from_address = configuration_helpers.get_value(
                    'email_from_address',
                    settings.DEFAULT_FROM_EMAIL
                )
                recipient_list = []
                if form.cleaned_data['send_to_students']:
                    recipient_list.append(student.user.email)
                if form.cleaned_data['send_to_parents']:
                    recipient_list.append(student.parents.first().user.email)

                if recipient_list:
                    send_mail("Due Date", txt_message, from_address, recipient_list, html_message=html_message)
                
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


def students_import(request):
    from csv import DictReader
    import_form = StudentImportForm()
    errors_list = []
    context = {
        'import_form': import_form,
        'errors_list': errors_list
    }
    if request.method == 'POST':
        import_form = StudentImportForm(request.POST, request.FILES)
        if import_form.is_valid():
            dataset = DictReader(import_form.cleaned_data['file_to_import'])
            role = 'student'
            for i, row in enumerate(dataset, 1):
                form_fields_map = {
                    'city': 'school_city',
                    'teacher_email': 'instructor',
                    'public_name': 'name'
                }
                form_data = {form_fields_map.get(k, k):v for k,v in row.items()}
                form_data['role'] = role
                form_data['password'] = User.objects.make_random_password()
                print(form_data)
                user_form = AccountImportValidationForm(form_data, tos_required=False)
                student_profile_form = StudentImportRegisterForm(form_data)
                if user_form.is_valid() and student_profile_form.is_valid():
                    if not student_profile_form.exists(form_data):
                        user, profile, registration = do_create_account(user_form, student_profile_form)

                else:
                    errors = {}
                    errors.update(dict(user_form.errors.items()))
                    errors.update(dict(student_profile_form.errors.items()))
                    print(errors)
                    errors_list.append((i, errors))
                    # error_list.append((i, user_form.errors.items() + student_profile_form.errors.items()))
        context.update(dict(
            row_data=row,
            # errors_list=errors_list
        ))
    return render(request, 'students_import.html', context)
