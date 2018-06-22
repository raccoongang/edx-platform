from .models import ExtraInfo
from django import forms


class ExtraInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExtraInfoForm, self).__init__(*args, **kwargs)

        self.fields['phone'].min_length = 9
        self.fields['phone'].placeholder = '?XXXXXXXX'

        self.fields['date_of_birth'].help_text = 'Please enter the date in this format "2000-09-01"'

        self.fields['user_role'].choices = ExtraInfo.USER_ROLES_CHOICES

    class Meta(object):
        model = ExtraInfo
        exclude = ['user', ]
        serialization_options = {
            'user_role': {
                'field_type': 'select'
            },
            'date_of_birth': {
                'field_type': 'text'
            }
        }

