"""
Defines the URL routes for ytp_api app.
"""

from django.conf.urls import patterns, url

from lms.djangoapps.ytp_api.views import CreateUserAccountWithoutPasswordView

urlpatterns = patterns(
    '',
    url(r'^api/user/create$', CreateUserAccountWithoutPasswordView.as_view()),
)
