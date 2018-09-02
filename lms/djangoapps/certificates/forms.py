from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _


class CertVerificationForm(forms.Form):
    certificate_uuid = forms.CharField(label=_('Certificate ID'), max_length=255, required=True)

