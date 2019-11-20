from datetime import datetime

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from opaque_keys.edx.keys import CourseKey
from pytz import utc

from calypso_reg_form.models import UserSpendTimeCourse
from courseware.models import UserCheckActivityConfig
from util.views import ensure_valid_course_key


@require_POST
@login_required
@ensure_valid_course_key
def set_spend_time(request, course_id):
    user = request.user
    course_key = CourseKey.from_string(course_id)
    page_close = json.loads(request.POST.get('page_close'))
    now = datetime.now(utc)
    user_check_activity_config = UserCheckActivityConfig.current()

    user_spend_time_course, created = UserSpendTimeCourse.objects.get_or_create(
        user=user,
        course_id=course_key
    )

    if user_spend_time_course.is_track:

        if user_spend_time_course.check_activity is not None:
            timedelta_check_activity = (now - user_spend_time_course.check_activity).seconds

            if timedelta_check_activity < user_check_activity_config.timeout_seconds:
                user_spend_time_course.spend_time += timedelta_check_activity

        user_spend_time_course.check_activity = None if page_close else now
        user_spend_time_course.save()

    return JsonResponse({"success": True})
