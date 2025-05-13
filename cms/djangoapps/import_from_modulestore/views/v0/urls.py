"""
Course to Library Import API v0 URLs.
"""

from django.urls import path

from .views import (
    ImportView,
)

app_name = 'v0'
urlpatterns = [
    path('import/', ImportView.as_view(), name='import'),
    path('import/<str:uuid>/', ImportView.as_view(), name='import_with_uuid'),
]
