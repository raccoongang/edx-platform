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


def get_program_filter(user_states):
    def _program_filter(p):
        _has_access = lambda c: any(k in user_states for k, v in c.us_state.iteritems() if v.get('approved', True) is not False)
        _filter = lambda c: hasattr(c, 'us_state') and _has_access(c)
        course_ids = map(lambda c: c.id.to_deprecated_string(), filter(_filter, modulestore().get_courses()))
        return all(all(cr['key'] in course_ids for cr in c.get('course_runs', [])) for c in p.get('courses', []))
    return _program_filter


@require_GET
def program_listing(request, user=None):
    """View a list of programs in which the user is engaged."""
    programs_config = ProgramsApiConfig.current()
    if not programs_config.enabled:
        raise Http404

    is_marketing = not bool(user)
    meter = ProgramProgressMeter(user=user or request.user)

    if is_marketing:
        user_states = []
        if hasattr(request.user, 'extrainfo'):
            user_states = request.user.extrainfo.stateextrainfo_set.all().values_list('state', flat=True)

        programs = filter(get_program_filter(user_states), meter.programs)
    else:
        programs = meter.engaged_programs

    mktg_url = lambda p: reverse('program_marketing_view', kwargs={'program_uuid': p['uuid']})
    [p.update({'marketing_page_url': mktg_url(p)}) for p in programs]

    context = {
        'disable_courseware_js': True,
        'marketing_url': get_program_marketing_url(programs_config),
        'nav_hidden': True,
        'programs': programs,
        'progress': meter.progress(programs),
        'show_program_listing': programs_config.enabled,
        'uses_pattern_library': True,
        'is_marketing': is_marketing
    }

    return render_to_response('learner_dashboard/programs.html', context)
