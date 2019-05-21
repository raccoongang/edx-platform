from .models import ExtraInfo
from django import forms


class ExtraInfoForm(forms.ModelForm):
    class Meta(object):
        model = ExtraInfo
        exclude = ['user', ]
