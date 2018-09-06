from django.http import Http404
from django.views.decorators.http import require_GET
from django.core.urlresolvers import reverse

from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import (
    ProgramProgressMeter,
    get_program_marketing_url
)


@require_GET
def program_listing(request, user=None):
    """View a list of programs in which the user is engaged."""
    programs_config = ProgramsApiConfig.current()
    if not programs_config.enabled:
        raise Http404

    is_marketing = not bool(user)
    meter = ProgramProgressMeter(user=user or request.user)

    programs = is_marketing and meter.programs or meter.engaged_programs
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
