from .models import ExtraInfo
from django import forms


class ExtraInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExtraInfoForm, self).__init__(*args, **kwargs)
        self.fields['accepted_to_be_contacted'].required = True
        self.fields['accepted_to_be_contacted'].error_messages = {
            "required": u"You must accept to be contacted by email around Microsoft/Cloud products and Education "
        }

    class Meta:
        model = ExtraInfo
        exclude = ['user']
