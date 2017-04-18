from django import forms


class EventForm(forms.Form):
    """Form for Google Calendar event creation"""
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def create_event(self):
        """Performs Google Calendar API event.insert request"""
        print(self.cleaned_data)
        print('API REQUEST')
        pass
