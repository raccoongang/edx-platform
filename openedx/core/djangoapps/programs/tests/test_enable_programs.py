"""
Tests for the enable_programs management command.
"""
import ddt
from django.test import TestCase

from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.programs.management.commands import enable_programs
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration
from openedx.core.djangoapps.site_configuration.tests.factories import SiteFactory

LOGGER_NAME = 'openedx.core.djangoapps.programs.management.commands.enable_programs'


@ddt.ddt
class TestEnablePrograms(TestCase):
    """
    Tests for the enable_programs management command
    """
    def setUp(self):
        super(TestEnablePrograms, self).setUp()
        self.command = enable_programs.Command()
        self.site = SiteFactory()
        self.discovery_url = 'https://fake-discovery.com/api/v1/'
        self.service_user = 'fake_worker'

    def _check_configurations_updated(self):
        """
        Check that configurations exist and have the expected values.
        """
        conf_mapping = (
            (ProgramsApiConfig, {'enabled': True}),
            (CatalogIntegration, {
                'enabled': True,
                'internal_api_url': self.discovery_url,
                'service_username': self.service_user,
            })
        )
        for conf, values in conf_mapping:
            if not conf.equal_to_current(values):
                return False

        if SiteConfiguration.objects.get(
            site=self.site).site_values.get('COURSE_CATALOG_API_URL') != self.discovery_url:
            return False

        return True

    def _assert_succeeded(self):
        """
        Check the positive flow success.
        """
        self.command.handle(
            site_domain=self.site.domain, discovery_api_url=self.discovery_url, service_username=self.service_user
        )
        self.assertTrue(self._check_configurations_updated())

    def test_success(self):
        """
        Test the positive flow.
        """
        self._assert_succeeded()

    @ddt.data(
        (ProgramsApiConfig, {'enabled': True}, 0),
        (CatalogIntegration, {
            'enabled': True,
            'internal_api_url': 'https://fake-discovery.com/api/v1/',
            'service_username': 'fake_worker',
        }, 1)
    )
    @ddt.unpack
    def test_success_conf_already_exist(self, conf, fields, log_index):
        """
        Test command skipping existing config if it is up to date.
        """
        msg = '{} is up to date, skipping...'.format(conf.__name__)
        conf.objects.create(**fields)
        with self.assertLogs(logger=LOGGER_NAME, level='INFO') as cm:
            self._assert_succeeded()
            self.assertIn(msg, cm.output[log_index])

    def test_site_config_create(self):
        """
        Test command should create SiteConfiguration if it does not exists.
        """
        expected = {'COURSE_CATALOG_API_URL': self.discovery_url}
        msg = "Site configuration for '{site_name}' does not exist. Created a new one.".format(
            site_name=self.site.domain
        )
        with self.assertLogs(logger=LOGGER_NAME, level='INFO') as cm:
            self._assert_succeeded()
            self.assertIn(msg, cm.output[3])
            self.assertEqual(
                SiteConfiguration.objects.get(site=self.site).site_values,
                expected
            )

    def test_site_config_update(self):
        """
        Test command should not replace old values for SiteConfiguration.
        """
        SiteConfiguration.objects.create(site=self.site, site_values={'test_val': 'test_key'})
        expected = {'test_val': 'test_key', 'COURSE_CATALOG_API_URL': self.discovery_url}
        msg = "Found existing site configuration for '{site_name}'. Updating it.".format(site_name=self.site.domain)
        with self.assertLogs(logger=LOGGER_NAME, level='INFO') as cm:
            self._assert_succeeded()
            self.assertIn(msg, cm.output[3])
            self.assertEqual(
                SiteConfiguration.objects.get(site=self.site).site_values,
                expected
            )
