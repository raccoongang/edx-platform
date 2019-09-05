"""
Plugin configuration for integration settings in edx-platform.
"""
from __future__ import unicode_literals

from django.apps import AppConfig

from openedx.core.djangoapps.plugins.constants import ProjectType, PluginURLs, PluginSettings, SettingsType


class ApiConfig(AppConfig):
    name = u'ucdc_edx_api'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'ucdc_edx_api',
                PluginURLs.APP_NAME: u'ucdc_edx_api',
                PluginURLs.REGEX: r'^api/ucdc/',
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        },

        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.AWS: {PluginSettings.RELATIVE_PATH: 'settings.aws'},
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: 'settings.common'},
                SettingsType.DEVSTACK: {PluginSettings.RELATIVE_PATH: 'settings.devstack'},
                SettingsType.TEST: {PluginSettings.RELATIVE_PATH: 'settings.test'},
            },
        },

    }
