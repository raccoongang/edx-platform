"""
This module contains the admin configuration for the CourseToLibraryImport model.
"""
from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError

from . import api
from .data import CourseToLibraryImportStatus
from .models import CourseToLibraryImport

# Run a task to import courses to the library
# This task is run by the celery worker to import courses to the library.

COMPOSITION_LEVEL_CHOICES = (
    ('xblock', _('XBlock')),
    ('vertical', _('Unit')),
    ('sequential', _('Section')),
    ('chapter', _('Chapter')),
)


def _validate_block_keys(model_admin, request, block_keys_to_import):
    """
    Validate the block keys to import.
    """
    block_keys_to_import = block_keys_to_import.split(',')
    for block_key in block_keys_to_import:
        try:
            UsageKey.from_string(block_key)
        except InvalidKeyError:
            model_admin.message_user(
                request,
                _('Invalid block key: {block_key}').format(block_key=block_key),
                level=messages.ERROR,
            )
            return False
    return True


class CourseToLibraryImportActionForm(forms.Form):
    """
    Form for the CourseToLibraryImport action.
    """

    composition_level = forms.ChoiceField(
        choices=COMPOSITION_LEVEL_CHOICES,
        required=False,
        label='Composition Level'
    )
    override = forms.BooleanField(
        required=False,
        label='Override Existing Content'
    )
    block_keys_to_import = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Comma separated list of block keys to import.',
            'rows': 4
        }),
        required=False,
        label='Block Keys to Import'
    )


class CourseToLibraryImportAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CourseToLibraryImport model.
    """

    list_display = (
        'id',
        'status',
        'course_ids',
        'library_key',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'course_ids',
        'library_key',
    )

    raw_id_fields = ('user',)
    readonly_fields = ('status',)
    actions = ['import_course_to_library_action']

    def import_course_to_library_action(self, request, queryset):
        """
        Import selected courses to the library.
        """
        form = CourseToLibraryImportActionForm(request.POST or None)

        if request.POST and 'apply' in request.POST:
            if form.is_valid():
                block_keys_string = form.cleaned_data['block_keys_to_import']
                are_keys_valid = _validate_block_keys(self, request, block_keys_string)
                if not are_keys_valid:
                    return

                target_key_string = block_keys_string.split(',') if block_keys_string else []
                composition_level = form.cleaned_data['composition_level']
                override = form.cleaned_data['override']

                if not queryset.count() == queryset.filter(status=CourseToLibraryImportStatus.READY).count():
                    self.message_user(
                        request,
                        _('Only imports with status "Ready" can be imported to the library.'),
                        level=messages.ERROR,
                    )
                    return

                for obj in queryset:
                    for course_id in obj.course_ids.split():
                        api.import_library_from_staged_content(
                            library_key=obj.library_key,
                            user_id=request.user.pk,
                            usage_ids=target_key_string,
                            course_id=course_id,
                            import_id=str(obj.uuid),
                            composition_level=composition_level,
                            override=override,
                        )

                self.message_user(
                    request,
                    _('Importing courses to library.'),
                    level=messages.SUCCESS,
                )

                return HttpResponseRedirect(request.get_full_path())

        return TemplateResponse(
            request,
            'admin/custom_course_import_form.html',
            {
                'form': form,
                'queryset': queryset,
                'action_name': 'import_course_to_library_action',
                'title': _('Import Selected Courses to Library')
            }
        )

    import_course_to_library_action.short_description = _('Import selected courses to library')


admin.site.register(CourseToLibraryImport, CourseToLibraryImportAdmin)
