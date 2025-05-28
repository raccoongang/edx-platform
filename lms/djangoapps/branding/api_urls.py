"""
Branding API endpoint urls.
"""


from django.urls import path

from lms.djangoapps.branding.views import footer, IndexPageConfigView, waffle_flags

urlpatterns = [
    path('footer', footer, name="branding_footer"),
    path('waffle-flags', waffle_flags, name="branding_waffle_flags"),
    path('index', IndexPageConfigView.as_view(), name="index_page_config"),
]
