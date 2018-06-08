import cStringIO
import requests
from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import date

import xml.etree.ElementTree as ET

from django.conf import settings
from django import forms
from django.utils.translation import ugettext as _

from .models import ExtraInfo


class ExtraInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExtraInfoForm, self).__init__(*args, **kwargs)
        self.fields['mobile'].min_length = 9
        self.fields['mobile'].initial = '5XXXXXXXX'

        self.fields['nationality_id'].min_length = 10
        self.fields['nationality_id'].initial = _('Enter National ID')

        self.fields['date_of_birth_day'].label = _('Date of birth (Hijri)')
        self.fields['date_of_birth_day'].choices = (('', _('Day')), ) + tuple((x, x) for x in range(1, 31))
        self.fields['date_of_birth_month'].label = ''
        self.fields['date_of_birth_month'].choices = (('', _('Month')), ) + tuple((x, x) for x in range(1, 13))
        self.fields['date_of_birth_year'].label = ''
        self.fields['date_of_birth_year'].choices = (('', _('Year')), ) + tuple((x, x) for x in self._years_range())

    class Meta:
        model = ExtraInfo
        exclude = ['user', ]
        serialization_options = {
            'date_of_birth_day': {
                'field_type': 'select'
            },
            'date_of_birth_month': {
                'field_type': 'select'
            },
            'date_of_birth_year': {
                'field_type': 'select'
            }
        }

    def _years_range(self):
        g_to_i = lambda g: g - 622 + ((g - 622) / 32)
        current_year = date.today().year
        max_year = current_year - 4
        min_year = current_year - 100
        return xrange(g_to_i(min_year), g_to_i(max_year))

    def clean(self):
        cleaned_data = super(ExtraInfoForm, self).clean()
        self.validate_nic(cleaned_data)

    def validate_nic(self, cleaned_data):
        error_msg = _("Integration server is not available")

        integration_server_url = settings.FEATURES.get('INTEGRATION_SERVER_URL')
        integration_server_username = settings.FEATURES.get('INTEGRATION_SERVER_USERNAME')
        integration_server_password = settings.FEATURES.get('INTEGRATION_SERVER_PASSWORD')

        try:
            wsse = UsernameToken(integration_server_username, integration_server_password)
            client = Client(
                integration_server_url,
                wsse = wsse
            )
        except ValueError, requests.ConnectionError:
            self.add_error('nationality_id', forms.ValidationError(error_msg, code='invalid'))
            return None

        date_of_birth = '{}{}{}'.format(
            cleaned_data['date_of_birth_year'],
            str(cleaned_data['date_of_birth_month']).rjust(2, '0'),
            str(cleaned_data['date_of_birth_day']).rjust(2, '0')
            )
        methods = {
            'CitizenRecordInfoBrief': {
                'nationalID': cleaned_data['nationality_id'],
                'dateOfBirth': date_of_birth
            },
            'ResidentRecordInfoBrief': {
                'iqamaID': cleaned_data['nationality_id'],
                'rsidentBirthDate': date_of_birth
            }
        }

        result = {}

        for method_name, kwargs in methods.items():
            try:
                default = lambda *a, **k: {}
                method = getattr(client.service, method_name, default)
                result = method(**kwargs)

            except Exception:
                pass

            else:
                break

        if not result:
            msg = _(
                "Sorry, the information you provided is incorrect, please make sure you enter correct information")
            self.add_error('nationality_id', forms.ValidationError(msg, code='invalid'))
