"""
This module contains the admin configuration for the Import model.
"""
from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError
from openedx.core.djangoapps.content_libraries.api import ContentLibrary

from .api import import_course_staged_content_to_library
from .data import ImportStatus
from .models import Import, PublishableEntityImport, PublishableEntityMapping
from .tasks import save_legacy_content_to_staged_content_task


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
        'created',
        'status',
        'source_key',
        'target_change',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'source_key',
        'target_change',
    )

    raw_id_fields = ('user',)
    readonly_fields = ('status',)
    actions = ['import_course_to_library_action']

    def save_model(self, request, obj, form, change):
        """
        Launches the creation of Staged Content after creating a new import instance.
        """
        is_created = not getattr(obj, 'id', None)
        super().save_model(request, obj, form, change)
        if is_created:
            save_legacy_content_to_staged_content_task.delay_on_commit(obj.uuid)

    def import_course_to_library_action(self, request, queryset):
        """
        Import selected courses to the library.
        """
        form = ImportActionForm(request.POST or None)

        context = self.admin_site.each_context(request)
        context.update({
            'opts': self.opts,
            'form': form,
            'queryset': queryset,
            'action_name': 'import_course_to_library_action',
            'title': _('Import Selected Courses to Library'),
            'original': _('Import Courses to Library'),
        })

        if not form.is_valid():
            return TemplateResponse(request, 'admin/custom_course_import_form.html', context)

        if request.POST and 'apply' in request.POST:
            if not queryset.count() == queryset.filter(status=ImportStatus.STAGED).count():
                self.message_user(
                    request,
                    _('Only imports with status "Ready" can be imported to the library.'),
                    level=messages.ERROR,
                )
                return

            try:
                for obj in queryset:
                    import_course_staged_content_to_library(
                        form.cleaned_data['block_keys_to_import'].split(','),
                        str(obj.uuid),
                        form.cleaned_data['library'].learning_package_id,
                        request.user.pk,
                        composition_level=form.cleaned_data['composition_level'],
                        override=form.cleaned_data['override'],
                    )

                self.message_user(
                    request,
                    _('Importing courses to library.'),
                    level=messages.SUCCESS,
                )
            except ValueError as exc:
                self.message_user(
                    request,
                    _('Error importing courses to library: {}').format(exc),
                    level=messages.ERROR,
                )

            return HttpResponseRedirect(request.get_full_path())

        return TemplateResponse(request, 'admin/custom_course_import_form.html', context)

    import_course_to_library_action.short_description = _('Import selected courses to library')


admin.site.register(Import, ImportAdmin)
admin.site.register(PublishableEntityImport)
admin.site.register(PublishableEntityMapping)
