"""
URLs for mobile API
"""


from django.urls import include, path

from .views import OfflineXBlockStatusInfoView

urlpatterns = [
    path('xblocks_status_info/', OfflineXBlockStatusInfoView.as_view(), name='offline_xblocks_info'),
]
