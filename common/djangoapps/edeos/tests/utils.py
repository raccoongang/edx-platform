"""
Tests for the Edeos app utils.
"""

import unittest

from ddt import ddt, file_data, data, unpack

from edeos.utils import validate_wallets_data


@ddt
class DataUtilsTest(unittest.TestCase):
    """
    Test data-driven utils.
    """

    @file_data('resources/test_validate_wallets_data.json')
    def test_validate_wallets_data(self, data):
        """
        Test wallets data validators.
        """
        self.assertEqual(
            validate_wallets_data(
                wallet_name=data["wallet_name"],
                profitonomy_public_key=data["profitonomy_public_key"]
            ),
            data["result"]
        )
