"""
Defines the URL routes for sga_api app.
"""

from django.conf.urls import patterns, url

from lms.djangoapps.sga_api.views import CreateUserAccountWithoutPasswordView, BulkEnrollView

urlpatterns = patterns(
    '',
    url(r'^api/user/create$', CreateUserAccountWithoutPasswordView.as_view()),
    url(r'^api/user/bulkenrollment$', BulkEnrollView.as_view()),
)
