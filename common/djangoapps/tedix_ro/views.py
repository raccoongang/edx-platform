import datetime

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.urls import reverse
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from lms.djangoapps.instructor.enrollment import enroll_email
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollment
from student.helpers import get_next_url_for_login_page
from tedix_ro.forms import StudentEnrollForm
from tedix_ro.models import StudentProfile


def manage_courses(request):
    InstructorProfile = apps.get_model('tedix_ro', 'InstructorProfile')
    user = request.user
    if not user.is_authenticated():
        return redirect(get_next_url_for_login_page(request))

    if not user.is_staff:
        return redirect(reverse('dashboard'))

    context = {
        "csrftoken": csrf(request)["csrf_token"],
        'show_dashboard_tabs': True
    }
    try:
        students = user.instructorprofile.students.all()
    except InstructorProfile.DoesNotExist:
        return redirect(reverse('dashboard'))

    now = datetime.datetime.utcnow()
    courses = CourseOverview.objects.filter(enrollment_end__gt=now, enrollment_start__lt=now)
    form = StudentEnrollForm(students=students, courses=courses)

    if request.method == 'POST':
        data = dict(
            courses = map(CourseKey.from_string, request.POST.getlist('courses')),
            students = request.POST.getlist('students'),
            due_date = request.POST['due_date']
        )
        form = StudentEnrollForm(data=data, courses=courses, students=students)
        if form.is_valid():
            for course in form.cleaned_data['courses']:
                for student in form.cleaned_data['students']:
                    CourseEnrollment.enroll_by_email(student.user.email, course.id)

            messages.success(request, 'Students have been successfully enrolled.')
            return redirect(reverse('manage_courses'))

    context.update({
        'form': form
    })

    return render_to_response('manage_courses.html', context)
