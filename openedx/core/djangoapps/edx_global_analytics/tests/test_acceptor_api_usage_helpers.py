"""
Tests for OLGA acceptor api usage by edX global analytics application tasks and helper functions.
"""

import logging
import unittest
import uuid

import requests
from mock import patch

from openedx.core.djangoapps.edx_global_analytics.utils.token_utils import get_access_token

logger = logging.getLogger(__name__)


class TestAcceptorApiUsageHelpFunctions(unittest.TestCase):
    """
    Tests for OLGA acceptor api usage by edX global analytics application tasks and helper functions.
    """

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.request_exception_handler_with_logger')
    def test_decorator_if_no_exception(self, mock_request_exception_handler_with_logger):
        """
        Test request_exception_handler_with_logger return wrapped function, if Request Exception does not exist.
        """
        def mock_decorated_function(mock):
            """
            Mock decorated function.
            """
            return mock

        mock_request_exception_handler_with_logger.return_value = mock_decorated_function('mock')

        result = mock_request_exception_handler_with_logger()

        self.assertEqual(mock_decorated_function('mock'), result)

    @patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.logging.Logger.exception')
    @patch('openedx.core.djangoapps.edx_global_analytics.utils.utilities.request_exception_handler_with_logger')
    def test_decorator_if_exception(self, mock_request_exception_handler_with_logger, mock_logging_exception):
        """
        Test request_exception_handler_with_logger log exception if whatever happened with request.
        """
        mock_request_exception_handler_with_logger.return_value.side_effect = requests.RequestException()
        mock_logging_exception.exception.assert_called_once()

    @patch('openedx.core.djangoapps.edx_global_analytics.models.AccessTokensStorage.objects.first')
    def test_returning_token_if_token_exists(self, mock_access_tokens_storage_model_objects_first_method):
        """
        Verify that get_access_token gets access token from access tokens storage if it exists.
        """
        mock_access_token = uuid.uuid4().hex

        class MockAccessTokensStorageModelFirstObject(object):
            """
            Mock class for AccessTokensStorage model first object.
            """
            access_token = mock_access_token

        mock_access_tokens_storage_model_objects_first_method.return_value = MockAccessTokensStorageModelFirstObject()

        result = get_access_token()

        self.assertEqual(mock_access_token, result)

    @patch('openedx.core.djangoapps.edx_global_analytics.models.AccessTokensStorage.objects.first')
    def test_returning_empty_line_if_no_token(self, mock_access_tokens_storage_model_objects_first_method):
        """
        Verify that get_access_token return None if access token does not exist in access tokens storage.
        """
        mock_access_tokens_storage_model_objects_first_method.return_value = None
        result = get_access_token()

        self.assertEqual(None, result)
