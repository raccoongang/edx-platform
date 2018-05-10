from edxmako.shortcuts import render_to_response
from ci_program.models import Program
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.courseware.courses import get_course
from openedx.core.lib.courses import course_image_url


def show_programs(request, program_name):
    """
    Display the programs page
    """
    program = Program.objects.get(marketing_slug=program_name)
    
    courses = []
    for course_overview in program.get_courses():
        
        course_id = course_overview.id
        block_reference, _, location_as_string = str(course_id).partition(':')
        course_identifiers = location_as_string.split('+')
        org, key, run = course_identifiers[0], course_identifiers[1], course_identifiers[2]
        course_locator = CourseLocator(org, key, run)
        course_descriptor = get_course(course_locator)
        
        courses.append(
            {
                "course_key": course_id,
                "course": course_overview,
                "course_image": course_image_url(course_descriptor)
            }
        )

    context = {}
    context["program"] = program
    context["courses"] = courses
    return render_to_response('programs/programs.html', context)