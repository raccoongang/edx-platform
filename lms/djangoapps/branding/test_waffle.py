"""
Tests for toggles, where there is logic beyond enable/disable.
"""

from unittest.mock import patch
import ddt
from django.test import TestCase

from lms.djangoapps.branding.waffle import catalog_mfe_enabled


@ddt.ddt
class TestCatalogWaffle(TestCase):
    """
    Tests for catalog_mfe_enabled
    """

    @ddt.data(True, False)
    @patch("lms.djangoapps.branding.waffle.ENABLE_CATALOG_MFE")
    def test_catalog_mfe_enabled(
        self, is_waffle_enabled, mock_enable_catalog
    ):
        # Given Catalog MFE feature is / not enabled
        mock_enable_catalog.is_enabled.return_value = is_waffle_enabled

        # When I check if the feature is enabled
        is_catalog_mfe_enabled = catalog_mfe_enabled()

        # Then I respects waffle setting.
        self.assertEqual(is_catalog_mfe_enabled, is_waffle_enabled)
