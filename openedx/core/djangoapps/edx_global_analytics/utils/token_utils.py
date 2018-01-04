"""
Providers for access token`s authentication flow.
"""

import httplib

import requests

from openedx.core.djangoapps.edx_global_analytics.models import AccessTokensStorage
from openedx.core.djangoapps.edx_global_analytics.utils.utilities import request_exception_handler_with_logger


def clean_unauthorized_access_token():
    """
    Delete first and sole access token in storage.

    If instance unsuccessfully authorized, statistics dispatch flow needs to registry access token again.
    """
    AccessTokensStorage.objects.first().delete()


def get_access_token():
    """
    Return single access token for authorization.

    This application works only with single OLGA acceptor for now.
    So access token is needed to make relationship between `edx_global_analytics` and `OLGA`.
    Reference: https://github.com/raccoongang/acceptor
    """
    token_object = AccessTokensStorage.objects.first()

    if token_object:
        return token_object.access_token


@request_exception_handler_with_logger
def access_token_registration(olga_acceptor_url):
    """
    Request access token from OLGA and store it.
    """
    token_registration_request = requests.post(olga_acceptor_url + '/api/token/registration/')
    access_token = token_registration_request.json()['access_token']

    AccessTokensStorage.objects.create(access_token=access_token)

    return access_token


@request_exception_handler_with_logger
def access_token_authorization(access_token, olga_acceptor_url):
    """
    Verify that installation is allowed to send statistics to OLGA acceptor.

    If edX platform won't be authorized, method clear existing access token.
    Task will try to register a new token in next turn.
    """
    token_authorization_request = requests.post(
        olga_acceptor_url + '/api/token/authorization/', data={'access_token': access_token, }
    )

    if token_authorization_request.status_code == httplib.UNAUTHORIZED:
        clean_unauthorized_access_token()
        return

    return access_token


def get_acceptor_api_access_token(olga_acceptor_url):
    """
    Provide access token`s authentication flow for getting access token and return it.

    If access token does not exist, method goes to register it.
    After successful registration edX platform authorizes itself via access token.

    If instance successfully authorized, method returns access token.
    If not it cleans token in storage and goes ahead to repeat flow.
    """
    access_token = get_access_token()

    if not access_token:
        access_token = access_token_registration(olga_acceptor_url)

    return access_token_authorization(access_token, olga_acceptor_url)
