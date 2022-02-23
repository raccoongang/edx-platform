"""
Tests for email template_context
"""

from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings
from mock import Mock, patch

from openedx.core.djangoapps.ace_common.template_context import get_base_template_context
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration
from openedx.core.djangoapps.theming.models import SiteTheme


class GetBaseContextTestCase(TestCase):
    """
    Test getting template context
    """
    @override_settings(MICROSITE_SITE_THEME="ms-theme")
    @patch("django.conf.settings.DEFAULT_SITE_THEME", "edx-theme")
    def test_get_custom_theme_dir_for_template_context(self):
        """
        Tests that correct theme-dir is taken on template context for site with comprehensive theming
        """
        site = Site.objects.create(domain='ms-site.com', name='microsite')
        theme = 'ms-theme'
        SiteTheme.objects.get_or_create(site=site, theme_dir_name=theme)
        config = {
            "LMS_ROOT_URL": "http://{}".format(site.domain),
            "platform_name": "Microsite"
        }
        SiteConfiguration.objects.create(site=site, enabled=True, site_values=config)

        exp_logo_url = 'http://{}/static/{}/images/'.format(site.domain, theme)

        message_context = get_base_template_context(site)

        self.assertEqual(message_context['logo_url'], exp_logo_url)
        self.assertEqual(message_context['platform_name'], config['platform_name'])

    @override_settings(MICROSITE_SITE_THEME="ms-theme")
    @patch("django.conf.settings.DEFAULT_SITE_THEME", "edx-theme")
    def test_get_default_theme_dir_for_template_context(self):
        """
        Tests that default theme-dir is taken on template context for site with default theming
        """
        site = Site.objects.create(domain='ms1-site.com', name='microsite1')
        theme = 'edx-theme'
        config = {
            "LMS_ROOT_URL": "http://{}".format(site.domain),
            "platform_name": "Microsite1"
        }
        SiteConfiguration.objects.create(site=site, enabled=True, site_values=config)

        exp_logo_url = 'http://{}/static/{}/images/'.format(site.domain, theme)

        message_context = get_base_template_context(site)

        self.assertEqual(message_context['logo_url'], exp_logo_url)
        self.assertEqual(message_context['platform_name'], config['platform_name'])
