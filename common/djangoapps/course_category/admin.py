from django.conf import settings
from django.contrib import admin
from django.contrib.admin.actions import delete_selected as delete_selected_original
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _

from course_category.models import CourseCategory


def delete_selected(modeladmin, request, queryset):
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    if request.POST.get('post'):
        for obj in queryset:
            obj.delete()
    else:
        return delete_selected_original(modeladmin, request, queryset)


delete_selected.short_description = _("Delete selected objects")


class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    readonly_fields = ('courses',)
    actions = [delete_selected]


if settings.FEATURES.get('ENABLE_COURSE_CATEGORIES'):
    admin.site.register(CourseCategory, CourseCategoryAdmin)
