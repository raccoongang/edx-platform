"""
Branding API endpoint urls.
"""


from django.urls import path

from lms.djangoapps.branding.views import footer, FrontendConfigView

urlpatterns = [
    path('footer', footer, name="branding_footer"),
    path('frontend-config', FrontendConfigView.as_view(), name="frontend_config"),
]
