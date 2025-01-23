"""
OAuth2 wrapper urls
"""


from django.conf import settings
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from mobile_api_extensions.views import AuthorizationCodeExchangeView
from mobile_api_extensions.utils import is_enabled_mobile

from . import views

urlpatterns = [
    re_path(r'^authorize/?$', csrf_exempt(views.AuthorizationView.as_view()), name='authorize'),
    re_path(r'^access_token/?$', csrf_exempt(views.AccessTokenView.as_view()), name='access_token'),
    re_path(r'^revoke_token/?$', csrf_exempt(views.RevokeTokenView.as_view()), name='revoke_token'),
]

if settings.FEATURES.get('ENABLE_THIRD_PARTY_AUTH'):
    urlpatterns += [
        path('exchange_access_token/<str:backend>/', csrf_exempt(views.AccessTokenExchangeView.as_view()),
             name='exchange_access_token',
             ),
    ]

if is_enabled_mobile():
    urlpatterns.append(
        re_path(
            r'^exchange_authorization_code/?$',
            csrf_exempt(AuthorizationCodeExchangeView.as_view()),
            name='exchange_authorization_code',
        )
    )
