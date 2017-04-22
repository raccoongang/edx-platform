from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/calendar']

# TODO: add some consperancy here:
credentials = ServiceAccountCredentials.from_json_keyfile_name(
            '/edx/app/edxapp/edx-platform/openedx/features/djangoapps/calendar_tab/openedx-google-calendar-private-key.json',
            scopes)

gcal_service = build('calendar', 'v3', credentials=credentials)


def publish_calendar(calendar_id):
    """Makes google calendar public by its ID"""
    rule = {
        'scope': {
            'type': 'default',
        },
        'role': 'reader'
    }
    created_rule = gcal_service.acl().insert(calendarId=calendar_id, body=rule).execute()
    return created_rule
