from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/calendar']

try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        settings.FEATURES['GOOGLE_CALENDAR_TAB_PRIVATE_KEY_URL'], scopes)
except (IOError, KeyError) as e:
    raise ImproperlyConfigured(
        "You must set `FEATURES['GOOGLE_CALENDAR_TAB_PRIVATE_KEY_URL']` when "
        "`FEATURES['ENABLE_CALENDAR']` is True."
    )

gcal_service = build('calendar', 'v3', credentials=credentials)


# def publish_calendar(calendar_id):
#     """Makes google calendar public by its ID"""
#     rule = {
#         'scope': {
#             'type': 'default',
#         },
#         'role': 'reader'
#     }
#     created_rule = gcal_service.acl().insert(calendarId=calendar_id, body=rule).execute()
#     return created_rule
