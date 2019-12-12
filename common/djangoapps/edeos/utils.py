"""
Various utils for communication with Edeos API.
"""
import hashlib
import logging
import re
from urlparse import urlparse

from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from api_calls import ALLOWED_EDEOS_API_ENDPOINTS_NAMES, EdeosApiClient
from configs import (
    EDEOS_STUDIO_FIELDS,
    WALLET_NAME_LENGTH,
    PROFITONOMY_PUBLIC_KEY_LENGTH_INTERVAL,
)

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
        log.info("Data to be sent to Edeos endpoint {} - {}, api_scheme_host - {}, api_path - {}, client id (auth) - {}".
                 format(api_endpoint, kwargs.get('payload'), api_scheme_host, api_path, kwargs.get("key")))
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

def get_user_id(user_model):
    """
    Generate users unique id by user object.

    :return: the md5 hash of the user's id.
    """
    m = hashlib.md5()
    m.update(str(user_model.id))
    return m.hexdigest()

def get_user_id_from_email(user_email):
    """
    Generate users unique id by email of the user.
    """
    return get_user_id(User.objects.get(email = user_email))

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
            user = getattr(model_obj, "user", getattr(model_obj, "student", None))
            uid = ""
            if event_type == 3 or event_type == 4:
                uid = unicode(model_obj.module_state_key)
            payload = {
                'student_id': user and get_user_id(user) or '',
                'course_id': course_id,
                'org': org,
                'client_id': course.edeos_key,
                'event_type': event_type,
                'event_details': event_details
            }
            if uid:
                payload['uid'] = uid
            data = {
                'payload': payload,
                'secret': course.edeos_secret,
                'key': course.edeos_key,
                'base_url': course.edeos_base_url,
                'api_endpoint': 'transactions_store'
            }
            return data
    return None


def validate_wallets_data(wallet_name, profitonomy_public_key):
    """
    Validate wallets data.

    Rules:
        both: length strict check, non-empty
        wallet_name:
            length equals to 12,
            all symbols lowercase,
            all numbers (value 1 to 5),
            order (symbols/numbers) does'n metter,
            no special characters (should be alphanumeric).

    Arguments:
          wallet_name (str): wallet name, e.g. "mywallet"
          profitonomy_public_key (str): public key, e.g.
              ```
              EOS7qFLiLsdYYogZUbqNGnQVdn7YBiYeDPoadTDHGLEFi6kxtBb8u1111111111s
              ```
    """
    return (
        # Only lowercase letters and digits (1 to 5)
        bool(re.match("^[a-z1-5]*$", wallet_name.strip()))
        and len(wallet_name.strip()) == WALLET_NAME_LENGTH
        and (
            PROFITONOMY_PUBLIC_KEY_LENGTH_INTERVAL[0]
            <= len(profitonomy_public_key.strip())
            <= PROFITONOMY_PUBLIC_KEY_LENGTH_INTERVAL[1]
        )
    )
