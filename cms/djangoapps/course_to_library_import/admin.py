from django.contrib import admin

from .models import CourseToLibraryImport

# Run a task to import courses to the library
# This task is run by the celery worker to import courses to the library.


admin.site.register(CourseToLibraryImport)
