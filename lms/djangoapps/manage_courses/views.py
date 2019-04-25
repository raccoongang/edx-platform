import datetime

from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from edxmako.shortcuts import render_to_response

from student.helpers import get_next_url_for_login_page
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


def manage_courses(request):
    InstructorProfile = apps.get_model('tedix_ro', 'InstructorProfile')
    redirect_to = get_next_url_for_login_page(request)
    user = request.user
    if not user.is_authenticated():
        return redirect(redirect_to)

    if not user.is_staff:
        return redirect(reverse('dashboard'))

    context = {
        'show_dashboard_tabs': True
    }

    try:
        students = user.instructorprofile.students.all()
        context.update({
            'students': students
        })
    except InstructorProfile.DoesNotExist:
        return redirect(reverse('dashboard'))

    now = datetime.datetime.utcnow()
    courses = CourseOverview.objects.filter(enrollment_end__gt=now, enrollment_start__lt=now)

    context.update({
        'courses': courses
    })

    return render_to_response('manage_courses.html', context)
