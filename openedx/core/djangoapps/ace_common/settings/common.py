"""
Settings for ace_common app.
"""
from openedx.core.djangoapps.ace_common.utils import setup_firebase_app

ACE_ROUTING_KEY = 'edx.lms.core.default'


def plugin_settings(settings):  # lint-amnesty, pylint: disable=missing-function-docstring, missing-module-docstring
    if 'push_notifications' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('push_notifications')
    settings.ACE_ENABLED_CHANNELS = [
        'django_email'
    ]
    settings.ACE_ENABLED_POLICIES = [
        'bulk_email_optout'
    ]
    settings.ACE_CHANNEL_SAILTHRU_DEBUG = True
    settings.ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME = 'Automated Communication Engine Email'
    settings.ACE_CHANNEL_SAILTHRU_API_KEY = None
    settings.ACE_CHANNEL_SAILTHRU_API_SECRET = None
    settings.ACE_CHANNEL_DEFAULT_EMAIL = 'django_email'
    settings.ACE_CHANNEL_TRANSACTIONAL_EMAIL = 'django_email'

    settings.ACE_ROUTING_KEY = ACE_ROUTING_KEY

    settings.FEATURES['test_django_plugin'] = True
    settings.FCM_APP_NAME = 'fcm-edx-platform'

    if getattr(settings, 'FIREBASE_SETTING_UP', None) is None:
        settings.ACE_CHANNEL_DEFAULT_PUSH = 'push_notification'

        # Note: To local development with Firebase, you must set FIREBASE_CREDENTIALS.
        settings.FCM_APP_NAME = 'fcm-edx-platform'
        settings.FIREBASE_CREDENTIALS = None

        if firebase_app := setup_firebase_app(settings.FIREBASE_CREDENTIALS, settings.FCM_APP_NAME):
            settings.ACE_ENABLED_CHANNELS.append(settings.ACE_CHANNEL_DEFAULT_PUSH)
            settings.ACE_ENABLED_POLICIES.append(settings.ACE_CHANNEL_DEFAULT_PUSH)

            settings.PUSH_NOTIFICATIONS_SETTINGS = {
                'CONFIG': 'push_notifications.conf.AppConfig',
                'APPLICATIONS': {
                    settings.FCM_APP_NAME: {
                        'PLATFORM': 'FCM',
                        'FIREBASE_APP': firebase_app,
                    },
                },
                'UPDATE_ON_DUPLICATE_REG_ID': True,
            }
            settings.FIREBASE_SETTING_UP = True
        else:
            settings.FIREBASE_SETTING_UP = False
