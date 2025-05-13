"""
This module contains the admin configuration for the Import model.
"""
from django import forms
from django.contrib import admin
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError
from openedx.core.djangoapps.content_libraries.api import ContentLibrary

from .forms import ImportCreateForm
from .models import Import, PublishableEntityImport, PublishableEntityMapping
from .tasks import import_course_to_library_task


COMPOSITION_LEVEL_CHOICES = (
    ('xblock', _('XBlock')),
    ('vertical', _('Unit')),
    ('sequential', _('Subsection')),
    ('chapter', _('Section')),
)


class ImportActionForm(forms.Form):
    """
    Form for the CourseToLibraryImport action.
    """

    library = forms.ModelChoiceField(queryset=ContentLibrary.objects.all(), required=False)
    block_keys_to_import = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Comma separated list of block keys to import.',
        }),
        required=False,
        label=_('Block Keys to Import'),
    )
    composition_level = forms.ChoiceField(
        choices=COMPOSITION_LEVEL_CHOICES,
        required=False,
        label=_('Composition Level')
    )
    override = forms.BooleanField(required=False, label=_('Override Existing Content'))

    def clean(self):
        cleaned_data = super().clean()
        required_together = ['block_keys_to_import', 'composition_level', 'library']
        values = [cleaned_data.get(field) for field in required_together]

        if not (all(values) or not any(values)):
            raise forms.ValidationError(
                _('Fields %(fields)s must be filled.'),
                code='invalid',
                params={'fields': ', '.join(required_together)},
            )

        try:
            [
                UsageKey.from_string(key.strip())
                for key in cleaned_data['block_keys_to_import'].split(',') if key.strip()
            ]
        except InvalidKeyError as exc:
            raise forms.ValidationError(
                _('Invalid block keys format.'),
                code='invalid',
            ) from exc

        return cleaned_data


class ImportAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Import model.
    """

    list_display = (
        'uuid',
        'state',
        'source_key',
        'target_change',
        'created',
    )
    list_filter = (
        'status__state',
    )
    search_fields = (
        'source_key',
        'target_change',
    )

    readonly_fields = ('status',)

    def uuid(self, obj):
        """
        Returns the UUID of the import.
        """
        return getattr(obj.status, 'uuid', None) if obj.status else None
    uuid.short_description = _('UUID')

    def state(self, obj):
        """
        Returns the state of the import.
        """
        return getattr(obj.status, 'state', None) if obj.status else None
    state.short_description = _('State')

    def created(self, obj):
        """
        Returns the creation date of the import.
        """
        return getattr(obj.status, 'created', None) if obj.status else None
    created.short_description = _('Created')

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return ImportCreateForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Launches the creation of Staged Content after creating a new import instance.
        """
        is_created = not getattr(obj, 'id', None)
        super().save_model(request, obj, form, change)
        if is_created:
            transaction.on_commit(lambda: import_course_to_library_task.delay(
                    obj.pk,
                    form.cleaned_data['usage_keys_string'].split(','),
                    form.cleaned_data['library'].learning_package_id,
                    obj.user.pk,
                    composition_level=form.cleaned_data['composition_level'],
                    override=form.cleaned_data['override'],
                )
            )


admin.site.register(Import, ImportAdmin)
admin.site.register(PublishableEntityImport)
admin.site.register(PublishableEntityMapping)
