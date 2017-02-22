"""
Django URLs for service status app
"""
from django.conf.urls import patterns, url
from views import user_referral

urlpatterns = patterns(
    '',
    url(r'^(?P<hashkey>[^/]*)$', user_referral, name='user_referral'),
)
