"""
Branding API endpoint urls.
"""


from django.urls import path

from lms.djangoapps.branding.views import footer, LMSFrontendParamsView
from openedx.core.constants import COURSE_ID_PATTERN

urlpatterns = [
    path('footer', footer, name="branding_footer"),
    path('frontend-params', LMSFrontendParamsView.as_view(), name="frontend_params"),
]
