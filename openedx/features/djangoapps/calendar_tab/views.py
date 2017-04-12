from django.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_with_access


def calendar_view(request, course_id):
    """Renders calendar tab in course navigation"""
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)

    context = {
        "course": course,
    }
    return render_to_response("calendar_tab/calendar_tab_page.html", context)
