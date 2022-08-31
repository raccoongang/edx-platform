"""Organizations views for use with Studio."""


from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from organizations.api import get_organizations

from cms.djangoapps.course_creators.models import CourseCreator
from openedx.core.djangolib.js_utils import dump_js_escaped_json


class OrganizationListView(View):
    """View rendering organization list as json.

    This view renders organization list json which is used in org
    autocomplete while creating new course.
    """

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        """Returns organization list as json."""
        org_names_list = []

        course_creator = CourseCreator.objects.filter(user=request.user).last()
        is_state_granted = course_creator and course_creator.state == CourseCreator.GRANTED
        organizations = get_organizations()

        if request.user.is_staff or (is_state_granted and course_creator.all_organizations):
            org_names_list = [(org["short_name"]) for org in organizations]
        elif is_state_granted:
            org_names_list = list(course_creator.member_of_organizations_name())

        return HttpResponse(dump_js_escaped_json(org_names_list), content_type='application/json; charset=utf-8')  # lint-amnesty, pylint: disable=http-response-with-content-type-json
