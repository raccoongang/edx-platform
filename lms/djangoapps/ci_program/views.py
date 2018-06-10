from django.contrib.auth.decorators import login_required
from edxmako.shortcuts import render_to_response
from ci_program.models import Program
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.courseware.courses import get_course
from openedx.core.lib.courses import course_image_url


@login_required
def show_programs(request, program_name):
    """
    Display the programs page
    """
    program = Program.objects.get(marketing_slug=program_name)
    program_descriptor = program.get_program_descriptor(request.user)

    context = {}
    context["program"] = program_descriptor
    return render_to_response('programs/programs.html', context)