"""
This module contains the admin configuration for the CourseToLibraryImport model.
"""

from django.contrib import admin

from .forms import CourseToLibraryImportForm
from .models import CourseToLibraryImport

# Run a task to import courses to the library
# This task is run by the celery worker to import courses to the library.


class CourseToLibraryImportAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CourseToLibraryImport model.
    """

    list_display = (
        'id',
        'status',
        'course_ids',
        'library_key',
        'source_type',
    )
    list_filter = (
        'status',
        'source_type',
    )
    search_fields = (
        'course_ids',
        'library_key',
    )

    form = CourseToLibraryImportForm


admin.site.register(CourseToLibraryImport, CourseToLibraryImportAdmin)
