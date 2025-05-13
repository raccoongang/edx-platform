from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.auth import get_user_model
from openedx.core.djangoapps.content_libraries.api import ContentLibrary

from .data import CompositionLevel
from .models import Import as _Import


User = get_user_model()
admin.autodiscover()

class ImportCreateForm(forms.ModelForm):
    """
    Form for creating an Import instance.
    """
    class Meta:
        model = _Import
        fields = ['source_key', 'target_change', 'user']

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label='User',
        widget=ForeignKeyRawIdWidget(_Import._meta.get_field('user').remote_field, admin.site)
    )
    usage_keys_string = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Comma separated list of usage keys to import.',
        }),
        required=True,
        label='Usage Keys to Import',
    )
    library = forms.ModelChoiceField(queryset=ContentLibrary.objects.all(), required=False)
    composition_level = forms.ChoiceField(
        choices=CompositionLevel.choices(),
        required=True,
        label='Composition Level'
    )
    override = forms.BooleanField(required=False, label='Override Existing Content')
