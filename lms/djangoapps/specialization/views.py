"""Organizations views for use with Studio."""
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import HttpResponse

from openedx.core.djangolib.js_utils import dump_js_escaped_json
from django.shortcuts import render
from lms.djangoapps.specialization.models import specializations
from organizations.models import Organization
from django.core.exceptions import ObjectDoesNotExist

class SpeializationListView(View):
    """View rendering organization list as json.

    This view renders organization list json which is used in org
    autocomplete while creating new course.
    """

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Returns organization list as json."""
        specialzations = specializations.objects.all()
        specz_names_list = [(specz["short_name"]) for specz in specialzations]
        return HttpResponse(dump_js_escaped_json(specz_names_list), content_type='application/json; charset=utf-8')

# Create your views here.
def specializationName(specId):
    specname = ''
    try:
        getDetails = specializations.objects.get(id=specId)
        specname = getDetails.name
    except ObjectDoesNotExist:
        getDetails = None

    return specname

def organizationName(orgId):
    orgname = ''
    try:
        getDetails = Organization.objects.get(id=orgId)
        orgname = getDetails.name
    except ObjectDoesNotExist:
        getDetails = None