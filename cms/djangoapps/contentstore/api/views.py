""" API v0 views. """

import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from student.auth import  has_studio_read_access
from course_action_state.models import CourseRerunState, CourseRerunUIStateManager
from django.http import JsonResponse

log = logging.getLogger(__name__)


@login_required
@require_POST
def check_rerun_courses(request):
    courses_ids = request.POST.get('courses', [])
    rerun_courses_keys = [
        course.course_key for course in
        CourseRerunState.objects.find_all(
            exclude_args={'state': CourseRerunUIStateManager.State.SUCCEEDED},
            should_display=True,
        )
        if has_studio_read_access(request.user, course.course_key)
    ]

    if rerun_courses_keys and courses_ids:
        for id in courses_ids:
            if id not in rerun_courses_keys:
                break;
        else:
            return JsonResponse({'is_reload': False})

    return JsonResponse({'is_reload': True})