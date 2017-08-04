"""
Tests acceptor API usage by edx global analytics application functions aka utils.
"""

import httplib
import unittest
import uuid

from ddt import ddt, data, unpack
from mock import patch, call

from openedx.core.djangoapps.edx_global_analytics.utils.utilities import send_instance_statistics_to_acceptor
from openedx.core.djangoapps.edx_global_analytics.utils.token_utils import (
    access_token_authorization,
    access_token_registration,
)


@ddt
@patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.requests.post')
class TestAcceptorApiUsage(unittest.TestCase):
    """
    Test functionality for acceptor API usage.
    """

    def tests_sending_requests(self, mock_request):
        """
        Tests to prove that methods send request to needed corresponding URLs.
        """

        # Verify that access_token_registration sends request to acceptor API for token registration.
        access_token_registration('https://mock-url.com')

        # Verify that access_token_authorization sends request to acceptor API for token authorization.
        mock_access_token = uuid.uuid4().hex
        access_token_authorization(mock_access_token, 'https://mock-url.com')

        # Verify that send_instance_statistics_to_acceptor sends request to acceptor API for token dispatch statistics.
        send_instance_statistics_to_acceptor('https://mock-url.com', {'mock_data': 'mock_data', })

        expected_calls = [
            call('https://mock-url.com/api/token/registration/'),
            call('https://mock-url.com/api/token/authorization/', data={'access_token': mock_access_token}),
            call('https://mock-url.com/api/installation/statistics/', {'mock_data': 'mock_data'}),
        ]

        self.assertEqual(mock_request.call_args_list, expected_calls)

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.logging.Logger.info')
    @data(
        [httplib.CREATED, 'Data were successfully transferred to OLGA acceptor. Status code is {0}.'],
        [httplib.BAD_REQUEST, 'Data were not successfully transferred to OLGA acceptor. Status code is {0}.']
    )
    @unpack
    def test_sent_statistics(self, status_code, log_message, mock_logging, mock_request):
        """
        Verify that send_instance_statistics_to_acceptor successfully dispatches statistics to acceptor API.
        """
        mock_request.return_value.status_code = status_code

        send_instance_statistics_to_acceptor('https://mock-url.com', {'mock_data': 'mock_data', })

        mock_logging.assert_called_with(
            log_message.format(mock_request.return_value.status_code)
        )
