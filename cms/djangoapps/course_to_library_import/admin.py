"""
This module contains the admin configuration for the CourseToLibraryImport model.
"""
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.utils.translation import gettext_lazy as _

from opaque_keys.edx.keys import CourseKey, UsageKey
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

class CourseToLibraryImportActionForm(ActionForm):
    composition_level = forms.ChoiceField(choices=COMPOSITION_LEVEL_CHOICES)
    override = forms.BooleanField(required=False)
    block_keys_to_import = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _('Comma separated list of block keys to import.')}),
    )

    def clean_block_keys_to_import(self):
        block_keys_to_import = self.cleaned_data.get('block_keys_to_import', '').split(',')
        for block_key in block_keys_to_import:
            try:
                UsageKey.from_string(block_key)
            except InvalidKeyError:
                raise forms.ValidationError(_('Invalid block key: {block_key}').format(block_key=block_key)) # FIXME: errormessage doesn't show up


@admin.action(description="Import course 2 library")
def import_course_to_library_action(model_admin, request, queryset):
    target_key_string = request.POST.get('block_keys_to_import', '').split(',')
    composition_level = request.POST['composition_level']
    override = request.POST.get('override', False)

    if not queryset.count() == queryset.filter(status=CourseToLibraryImportStatus.READY).count():
        model_admin.message_user(
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

        # TODO: target_key_string can refer to different imports, so you need
        # to do something about validation, which is designed for one import and only its blocks.

        # Traceback:
        # ValueError('Block block-v1:org+2+2025+type@chapter+block@3f8c073c6bf74096b9a4033227de01d3 is not available for import')
        # Traceback (most recent call last):
        #   File "/openedx/venv/lib/python3.11/site-packages/celery/app/trace.py", line 453, in trace_task
        #     R = retval = fun(*args, **kwargs)
        #                  ^^^^^^^^^^^^^^^^^^^^
        #   File "/openedx/venv/lib/python3.11/site-packages/edx_django_utils/monitoring/internal/code_owner/utils.py", line 195, in new_function
        #     return wrapped_function(*args, **kwargs)
        #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/openedx/edx-platform/cms/djangoapps/course_to_library_import/tasks.py", line 76, in import_library_from_staged_content_task
        #     validate_usage_ids(usage_ids, staged_content)
        #   File "/openedx/edx-platform/cms/djangoapps/course_to_library_import/validators.py", line 41, in validate_usage_ids
        #     raise ValueError(f'Block {usage_key} is not available for import')
        # ValueError: Block block-v1:org+2+2025+type@chapter+block@3f8c073c6bf74096b9a4033227de01d3 is not available for import



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
    actions = (import_course_to_library_action,)
    action_form = CourseToLibraryImportActionForm


admin.site.register(CourseToLibraryImport, CourseToLibraryImportAdmin)
