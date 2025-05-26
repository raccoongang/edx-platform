"""
Branding API endpoint urls.
"""


from django.urls import path

from lms.djangoapps.branding.views import footer, IndexPageConfigView, WaffleFlagsView

urlpatterns = [
    path('footer', footer, name="branding_footer"),
    path('waffle-flags', WaffleFlagsView.as_view(), name="branding_waffle_flags"),
    path('index', IndexPageConfigView.as_view(), name="index_page_config"),
]
