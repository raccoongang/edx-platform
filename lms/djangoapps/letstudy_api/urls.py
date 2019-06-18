"""
Defines the URL routes for letstudy_api app.
"""

from django.conf.urls import url

from .views import CreateUserAccountWithoutPasswordView, UserEnrollView

urlpatterns = [
    url(r'^create$', CreateUserAccountWithoutPasswordView.as_view()),
    url(r'^enroll$', UserEnrollView.as_view()),
]
