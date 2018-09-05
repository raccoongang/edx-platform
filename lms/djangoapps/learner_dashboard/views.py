"""Learner dashboard views"""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.decorators.http import require_GET

from edxmako.shortcuts import render_to_response
from lms.djangoapps.learner_dashboard.utils import FAKE_COURSE_KEY, strip_course_id
from openedx.core.djangoapps.catalog.utils import get_programs
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import (
    ProgramDataExtender,
    ProgramProgressMeter,
    get_certificates,
    get_program_marketing_url
)
from openedx.core.djangoapps.programs.views import program_listing as base_program_listing
from openedx.core.djangoapps.user_api.preferences.api import get_user_preferences
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment


@login_required
def program_listing(request):
    return base_program_listing(request, request.user)


def get_course_ids(courses):
    course_ids = []
    for course in courses:
        course_ids.extend([CourseKey.from_string(c['key']) for c in course['course_runs']])
    return course_ids


@login_required
@require_GET
def program_details(request, program_uuid):
    """View details about a specific program."""
    programs_config = ProgramsApiConfig.current()
    if not programs_config.enabled:
        raise Http404

    meter = ProgramProgressMeter(request.user, uuid=program_uuid)
    program_data = meter.programs[0]

    if not program_data:
        raise Http404

    program_data = ProgramDataExtender(program_data, request.user).extend()
    course_data = meter.progress(programs=[program_data], count_only=False)[0]
    certificate_data = get_certificates(request.user, program_data)

    course_ids = get_course_ids(program_data.pop('courses'))
    total_courses_count = len(course_ids)

    started_courses_count = CourseEnrollment.enrollments_for_user(request.user).filter(course_id__in=course_ids).count()

    if started_courses_count:
        program_data['price'] = '%.2f' % ((float(program_data['price']) / total_courses_count) * (total_courses_count - started_courses_count))

    urls = {
        'program_listing_url': reverse('program_listing_view'),
        'track_selection_url': strip_course_id(
            reverse('course_modes_choose', kwargs={'course_id': FAKE_COURSE_KEY})
        ),
        'commerce_api_url': reverse('commerce_api:v0:baskets:create'),
    }

    context = {
        'urls': urls,
        'show_program_listing': programs_config.enabled,
        'nav_hidden': True,
        'disable_courseware_js': True,
        'uses_pattern_library': True,
        'user_preferences': get_user_preferences(request.user),
        'program_data': program_data,
        'course_data': course_data,
        'certificate_data': certificate_data,
        'add_to_cart_url': reverse('add_programm_to_cart', kwargs={'uuid': program_data['uuid']}),
    }

    return render_to_response('learner_dashboard/program_details.html', context)
