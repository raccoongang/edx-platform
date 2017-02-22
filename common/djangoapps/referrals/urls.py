"""
Django URLs for service status app
"""
from django.conf.urls import url
from views import user_referral

urlpatterns = [
    url(r'^(?P<hashkey>[^/]*)$', user_referral, name='user_referral'),
]
