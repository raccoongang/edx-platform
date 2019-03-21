"""
Various utils for communication with Edeos API.
"""
import logging
from urlparse import urlparse

from django.contrib.sites.models import Site
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from api_calls import ALLOWED_EDEOS_API_ENDPOINTS_NAMES, EdeosApiClient
from configs import EDEOS_STUDIO_FIELDS

log = logging.getLogger(__name__)


def get_balance(request):
    return 120


def send_edeos_api_request(**kwargs):
    """
    Initialize Edeos API client and perform respective call.
    """
    api_scheme_host = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(kwargs.get('base_url')))
    api_path = '{uri.path}'.format(uri=urlparse(kwargs.get('base_url')))
    edeos_client = EdeosApiClient(client_id=kwargs.get("key"),
                                  client_secret=kwargs.get("secret"),
                                  api_scheme_host=api_scheme_host,
                                  api_path=api_path)
    api_endpoint = kwargs.get("api_endpoint")
    if api_endpoint in ALLOWED_EDEOS_API_ENDPOINTS_NAMES:
        log.info("Data to be sent to Edeos endpoint {} - {}, api_scheme_host - {}, api_path - {}".
                 format(api_endpoint, kwargs.get('payload'), api_scheme_host, api_path))
        endpoint_to_call = getattr(edeos_client, api_endpoint)
        response = endpoint_to_call(payload=kwargs.get('payload'))
        return response
    else:
        log.exception("Disallowed Edeos endpoint name: '{}'".format(api_endpoint))
        return None


def is_valid_edeos_field(fields):
    """
    Check if provided fields are valid.

    Arguments:
        fields (dict): fields to verify.
    Returns:
        verification result (bool)
    """
    for field in EDEOS_STUDIO_FIELDS:
        if not fields.get(field):
            log.error('Field "{}" is improperly configured.'.format(field))
            return False
    return True


# TODO: this could go as a mixin,
#  but note that it's used not only in `save()` now
def prepare_edeos_data(model_obj, event_type, event_details=None):
    """
    Prepare and send event data to Edeos.

    Data will be used as "transactions_store" endpoint payload.

    Arguments:
        model_obj (instance of a subclass of `django.db.models.Model`): object to collect
            event data from, e.g. `StudentModule` obj.
        event_type (int): type of event to send.
        event_details (dict): details on an event.
            # TODO prepare event types mapping
    """
    org = model_obj.course_id.org
    course_id = unicode(model_obj.course_id)
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)
    edeos_fields = {
        'edeos_secret': course.edeos_secret,
        'edeos_key': course.edeos_key,  # client id
        'edeos_base_url': course.edeos_base_url
    }
    if course.edeos_enabled:
        if is_valid_edeos_field(edeos_fields):
            student_id = ""
            if getattr(model_obj, "user", False):
                student_id = model_obj.user.email
            elif getattr(model_obj, "student", False):
                student_id = model_obj.student.email
            uid = ""
            if event_type == 1 or event_type == 2:
                uid = '{}_{}'.format(model_obj.user.pk, course_id)
            elif event_type == 3 or event_type == 4:
                uid = unicode(model_obj.module_state_key)
            payload = {
                'student_id': student_id,
                'course_id': course_id,
                'org': org,
                'client_id': course.edeos_key,
                'event_type': event_type,
                'uid': uid,
                'event_details': event_details
            }
            data = {
                'payload': payload,
                'secret': course.edeos_secret,
                'key': course.edeos_key,
                'base_url': course.edeos_base_url,
                'api_endpoint': 'transactions_store'
            }
            return data
    return None
