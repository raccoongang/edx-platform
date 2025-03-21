"""

"""
from django.urls import path

from cms.djangoapps.course_to_library_import.views.v0.views import (
    CreateCourseToLibraryImportView,
    GetCourseStructureToLibraryImportView
)

app_name = 'course_to_library_import'

urlpatterns = [
    path('v0/create-import/<str:lib_key_str>/', CreateCourseToLibraryImportView.as_view(), name='create_import'),
    path('v0/get-import/<uuid:course_to_lib_uuid>/', GetCourseStructureToLibraryImportView.as_view(), name='get_import'),
]
