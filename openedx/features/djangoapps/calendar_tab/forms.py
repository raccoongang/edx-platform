# -*- coding: utf-8 -*-
from django import forms

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build


class EventForm(forms.Form):
    """Form for Google Calendar event creation"""
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(widget=forms.Textarea, required=False)
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def create_event(self):
        """Performs Google Calendar API event.insert request"""

        scopes = ['https://www.googleapis.com/auth/calendar']
        # TODO: make credentials file configurable
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            '/edx/app/edxapp/edx-platform/openedx/features/djangoapps/calendar_tab/openedx-google-calendar-private-key.json',
            scopes)

        gcal_service = build('calendar', 'v3', credentials=credentials)

        # TODO: make calendar "dynamic"
        calendar_id = "o5i5gqd2s4sa3ngtt8td3qbqsg@group.calendar.google.com"
        event = {
            'summary': self.cleaned_data.get('title'),
            'location': self.cleaned_data.get('location') or '',
            'description': self.cleaned_data.get('description') or '',
            'start': {
                'dateTime': self.cleaned_data.get('start').isoformat(),
            },
            'end': {
                'dateTime': self.cleaned_data.get('end').isoformat(),
            },
        }

        gcal_service.events().insert(calendarId=calendar_id, body=event).execute()
