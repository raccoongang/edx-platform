"""
Defines the URL routes for ucdc app.
"""
from django.conf.urls import url

from ucdc_edx_api.api.views import RegisterAPIView

urlpatterns = [
    url(r'^user/create$', RegisterAPIView.as_view(), name="user_create"),
]
