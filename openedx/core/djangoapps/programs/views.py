from django.http import Http404
from django.views.decorators.http import require_GET
from django.core.urlresolvers import reverse

from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import (
    ProgramProgressMeter,
    get_program_marketing_url
)
from xmodule.modulestore.django import modulestore


def approved_states(course):
    return [k for k, v in course.us_state.iteritems() if v.get('approved', True) is not False]


def get_program_filter(user_states, courses=None):
    courses = courses or modulestore().get_courses()
    def _program_filter(p):
        _has_access = lambda c: any(s in user_states for s in approved_states(c))
        _filter = lambda c: hasattr(c, 'us_state') and _has_access(c)
        course_ids = map(lambda c: c.id.to_deprecated_string(), filter(_filter, courses))
        return all(all(cr['key'] in course_ids for cr in c.get('course_runs', [])) for c in p.get('courses', []))
    return _program_filter


def get_program_courses(program):
    courses = []
    [[courses.append(cr['key']) for cr in c.get('course_runs', [])] for c in program.get('courses', [])]
    return courses


@require_GET
def program_listing(request, user=None):
    """View a list of programs in which the user is engaged."""
    programs_config = ProgramsApiConfig.current()
    if not programs_config.enabled:
        raise Http404

    courses = modulestore().get_courses()
    is_marketing = not bool(user)

    type_fltr = request.GET.get('type')
    course_fltr = request.GET.get('course')

    meter = ProgramProgressMeter(user=user or request.user)

    user_states = []
    if is_marketing:
        user_states = []
        if hasattr(request.user, 'extrainfo'):
            user_states = request.user.extrainfo.stateextrainfo_set.all().values_list('state', flat=True)

        filters = [get_program_filter(user_states, courses=courses)]

        if type_fltr:
            filters.append(lambda p: p.get('bundle_type') in type_fltr.split(','))

        if course_fltr:
            filters.append(lambda p: all(c in get_program_courses(p) for c in course_fltr.split(',')))

        filter_ = lambda p: all(f(p) for f in filters)
        programs = filter(filter_, meter.programs)
    else:
        programs = meter.engaged_programs

    active_courses = []
    mktg_url = lambda p: reverse('program_marketing_view', kwargs={'program_uuid': p['uuid']})

    for p in programs:
        p.update({'marketing_page_url': mktg_url(p)})
        active_courses.extend(get_program_courses(p))

    _cf = lambda c: any(s in user_states for s in approved_states(c))
    courses = filter(_cf, courses)

    context = {
        'disable_courseware_js': True,
        'marketing_url': get_program_marketing_url(programs_config),
        'nav_hidden': True,
        'programs': programs,
        'progress': meter.progress(programs),
        'show_program_listing': programs_config.enabled,
        'uses_pattern_library': True,
        'is_marketing': is_marketing,
        'courses': courses,
        'active_courses': set(active_courses)
    }

    return render_to_response('learner_dashboard/programs.html', context)
