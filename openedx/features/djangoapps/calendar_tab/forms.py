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
    event_id = forms.CharField(widget=forms.HiddenInput, required=False)
    kill_event = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=False)
    calendar_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def create_event(self):
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
        try:
            response = gcal_service.events().insert(calendarId=self.cleaned_data['calendar_id'], body=event).execute()

        except Exception as e:
            # TODO: handle errors
            print(e)

    def delete_event(self):
        """Performs Google Calendar API event.insert request"""
        try:
            gcal_service.events().delete(calendarId=self.cleaned_data['calendar_id'],
                                         eventId=self.cleaned_data['event_id']).execute()
        except Exception as e:
            # TODO: handle errors
            print(e)
