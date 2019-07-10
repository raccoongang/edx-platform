from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from calypso_reg_form.models import ExtraInfo, StateExtraInfo


US_STATE_FORM_CHOICES = [(state_abbr, _(state_title)) for state_abbr, state_title in settings.US_STATE_CHOICES]
US_STATE_FORM_CHOICES.insert(0, ('', '--'))


class ExtraInfoForm(forms.ModelForm):
    # This is fake field just for represent the label,
    # because EDX registration form does not support fieldsets
    header_for_licenses = forms.CharField(label=_('State and License Information'),
                              required=False)

    state_1 = forms.ChoiceField(choices=US_STATE_FORM_CHOICES,
                              label=_('License State'),
                              required=True,
                              error_messages={'required': _('Please select your License State')})

    license_1 = forms.CharField(label=_('License Number'),
                              required=True,
                              error_messages={'required': _('Please enter your License')})
    state_2 = forms.ChoiceField(choices=US_STATE_FORM_CHOICES,
                              label=_('License State #2'),
                              required=False)

    license_2 = forms.CharField(label=_('License Number'),
                              required=False)
    state_3 = forms.ChoiceField(choices=US_STATE_FORM_CHOICES,
                              label=_('License State #3'),
                              required=False)

    license_3 = forms.CharField(label=_('License Number'),
                              required=False)

    class Meta:
        model = ExtraInfo
        exclude = ['user', ]
        serialization_options = {
            'header_for_licenses': {
                'field_type': 'hidden'
            }
        }

    def save_extra(self, commit=True):
        for n in [1, 2, 3]:
            state = self.cleaned_data.get('state_{}'.format(n))
            license = self.cleaned_data.get('license_{}'.format(n))
            if state and license:
                StateExtraInfo.objects.create(
                    extra_info=self.instance,
                    state=state,
                    license=license.strip()
                )

        return self.instance
