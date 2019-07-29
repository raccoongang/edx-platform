"""
Gate API clients logic.

For example, sending users' achievements to the Gate.
"""
import base64
import httplib
import logging
from urlparse import urlparse, urljoin

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from simplejson import JSONDecodeError

log = logging.getLogger(__name__)


ALLOWED_EDEOS_API_ENDPOINTS_NAMES = [
    "wallet_store",
    "wallet_update",
    "wallet_balance",
    "transactions",
    "transactions_store",
    "referrals_store",
    "statistics",
    "profile_statistics"
]


class EdeosApiBaseClientError(Exception):
    """
    Base class for Edeos API exceptions.

    Subclasses should provide `error_message`.
    """
    error_message = 'An exception occurred.'

    def __init__(self, detail=None):
        """
        Initialization of exceptions base class object.
        """
        self.detail = detail if detail is not None else self.error_message
        super(EdeosApiBaseClientError, self).__init__(detail)

    def __str__(self):
        """
        Override string representation of exceptions base class object.
        """
        return self.detail


class EdeosApiClientError(EdeosApiBaseClientError):
    error_message = 'Edeos API error occurred.'


class EdeosApiClientErrorUnauthorized(EdeosApiBaseClientError):
    error_message = 'Unauthorized call to Edeos API.'


class EdeosBaseApiClient(object):
    """
    Low-level Edeos API client.

    Sends requests to Edeos API directly.
    Responsible for API credentials issuing and `access_token` refreshing.

    Inspired by:
        https://github.com/raccoongang/xblock-video/blob/dev/video_xblock/backends/brightcove.py
    """
    def __init__(self, client_id, client_secret, api_address):
        """
        Initialize base Edeos API client.

        Arguments:
            client_id (str): Edeos client id.
            client_secret (str): Edeos client secret.
            api_address (url): Edeos Gate (API) address, e.g.
                "http://111.111.111.111/". It is configurable on Studio
                 and might change.
        """
        self.api_key = client_id
        self.api_secret = client_secret
        self.api_address = api_address
        if client_id and client_secret:
            self.access_token = self._refresh_access_token()
        else:
            self.access_token = ""

    def _refresh_access_token(self, scope=""):
        """
        Request new access token to send with requests to Edeos.

        Arguments:
            scope (str): OAuth permission scope.

        Returns:
            access_token (str): access token.
        """
        # TODO pre-configure domain
        url = urljoin(self.api_address, "oauth/token")
        params = {
            "grant_type": "client_credentials",
            "scope": scope
        }
        auth_string = base64.encodestring(
            '{}:{}'.format(self.api_key, self.api_secret)
        ).replace('\n', '')
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + auth_string
        }
        try:
            resp = requests.post(url, headers=headers, data=params)
            if resp.status_code == httplib.OK:
                result = resp.json()
                return result['access_token']
        except IOError:
            log.exception("Connection issue. Couldn't refresh Edeos API access token.")
            return None

    def post(self, url, payload, headers=None, can_retry=True):
        """
        Issue REST POST request to a given URL.

        Arguments:
            url (str): url to send a request to.
            payload (dict): request data.
            headers (dict): request headers.
            can_retry (bool): indication if requests sending should be retried.

        Returns:
              resp (dict): Edeos response.
        """
        headers_ = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if headers is not None:
            headers_.update(headers)
        resp = requests.post(url, json=payload, headers=headers_)
        log.info("Edeos response: status {}, content {}".format(resp.status_code, resp.content))
        if resp.status_code in (httplib.OK, httplib.CREATED):
            try:
                return resp.json()
            except JSONDecodeError:
                return resp

        elif resp.status_code == httplib.UNAUTHORIZED and can_retry:
            self.access_token = self._refresh_access_token()
            return self.post(url, payload, headers, can_retry=False)
        elif resp.status_code == httplib.UNAUTHORIZED:
            raise EdeosApiClientErrorUnauthorized
        else:
            raise EdeosApiClientError


class EdeosApiClient(EdeosBaseApiClient):
    """
    High-level Edeos API client.

    Communicates with Edeos API endpoints directly.
    """
    # TODO pass default `api_scheme_host` from settings
    def __init__(self, client_id, client_secret, api_scheme_host, api_path="api/point/v1/"):
        """
        Initialize high-level Edeos API client.

        Arguments:
            client_id (str): Edeos client id.
            client_secret (str): Edeos client secret.
            api_scheme_host (url): Edeos Gate (API) address, e.g.
                "http://111.111.111.111/". It is configurable on Studio
                 and might change.
            api_path (url): Edeos Gate (API) path, e.g.
                "api/point/v1/". It is configurable on Studio
                 and might change.
        """
        self.base_url = urljoin(api_scheme_host, api_path)
        super(EdeosApiClient, self).__init__(client_id, client_secret, api_scheme_host)

    def call_api(self, endpoint_url, payload):
        try:
            response = self.post(
                url="{}{}".format(self.base_url, endpoint_url),
                payload=payload)
            return response
        except (EdeosApiClientError, EdeosApiClientErrorUnauthorized) as e:
            print("Edeos '{}' call failed. {}".format(endpoint_url, e.__class__.error_message))
            return None
        except ValueError as e:
            log.exception("Edeos '{}' call failed. {}".format(endpoint_url, e.message))
            return None

    # TODO validate payload below (required/optional params)

    def wallet_store(self, payload):
        return self.call_api("wallet/store", payload)

    def wallet_update(self, payload):
        return self.call_api("wallet/update", payload)

    def wallet_balance(self, payload):
        return self.call_api("wallet/balance", payload)

    def transactions(self, payload):
        return self.call_api("transactions", payload)

    def transactions_store(self, payload):
        """
        Store new event data.

        Event examples: course enrollment, certificate issuing.

        Arguments:
             payload (dict): data on an event to send to Edeos, for example (extract of payload):
                 {
                     "student_id": "student@example.com",
                     "course_id": "course-v1:edX+DemoX+Demo_Course2",
                     "org": "edX",
                     "event_type": 1,
                     "event_details": {
                         "data1": "value",
                         "data2": "value",
                         "data3": 23
                     }
                 }
                 Note: `student_id` stands for a student who'll get tokens.

        Returns:
              response (dict): Edeos response.
        """
        return self.call_api("transactions/store", payload)

    def referrals_store(self, payload):
        """
        Store new referral.

        Arguments:
            payload (dict):  data on a referral, e.g.
                {
                    "student_id":"student@example.com",
                    "referral_id": "asdf@example.com",
                    "referral_type": "student_signup" | "course_enrollment",
                    "org": "edX",
                    "client_id":"5"
                }
        """
        return self.call_api("referrals/store", payload)

    def statistics(self, payload):
        return self.call_api("statistics", payload)
    
    def profile_statistics(self, payload):
        return self.call_api("profile_statistics", payload)
