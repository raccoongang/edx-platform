"""Learner dashboard views"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from edxmako.shortcuts import render_to_response

from lms.djangoapps.learner_dashboard.programs import ProgramDetailsFragmentView
from openedx.core.djangoapps.programs.views import program_listing as base_program_listing
from openedx.core.djangoapps.programs.models import ProgramsApiConfig


@login_required
def program_listing(request):
    return base_program_listing(request, request.user)


@login_required
@require_GET
def program_details(request, program_uuid):
    """View details about a specific program."""
    programs_config = ProgramsApiConfig.current()
    program_fragment = ProgramDetailsFragmentView().render_to_fragment(
        request, program_uuid, programs_config=programs_config
    )

    context = {
        'program_fragment': program_fragment,
        'show_program_listing': programs_config.enabled,
        'show_dashboard_tabs': True,
        'nav_hidden': True,
        'disable_courseware_js': True,
        'uses_pattern_library': True,
    }

    return render_to_response('learner_dashboard/program_details.html', context)
