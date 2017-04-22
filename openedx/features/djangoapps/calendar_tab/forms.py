# -*- coding: utf-8 -*-
from django import forms

from .utils import gcal_service


class EventForm(forms.Form):
    """Form for Google Calendar event creation"""
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(widget=forms.Textarea, required=False)
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def create_event(self, calendar_id):
        """Performs Google Calendar API event.insert request"""
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
