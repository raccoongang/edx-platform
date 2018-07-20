"""Url configuration for the auth module."""

from django.conf.urls import include, patterns, url
from django.conf import settings

from social_django.views import complete
from social_core.utils import setting_name

from .views import inactive_user_view, lti_login_and_complete_view, post_to_custom_auth_form, saml_metadata_view
from .decorators import signout_for_ws_federation


extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

urlpatterns = patterns(
    '',
    url(r'^auth/inactive', inactive_user_view, name="third_party_inactive_redirect"),
    url(r'^auth/custom_auth_entry', post_to_custom_auth_form, name='tpa_post_to_custom_auth_form'),
    url(r'^auth/saml/metadata.xml', saml_metadata_view),
    url(r'^auth/login/(?P<backend>lti)/$', lti_login_and_complete_view),
    url(r'^auth/complete/(?P<backend>[^/]+){0}$'.format(extra), signout_for_ws_federation(complete),
        name='social:complete'),

    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^auth/complete/(?P<backend>[^/]+){0}$'.format(extra), signout_for_ws_federation(complete),
        name='social:complete'),
)
