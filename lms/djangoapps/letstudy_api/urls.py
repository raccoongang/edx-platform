"""
Defines the URL routes for letstudy_api app.
"""

from django.conf.urls import url

from .views import CreateUserAccountWithoutPasswordView, UserEnrollView

urlpatterns = [
    url(r'^api/user/create$', CreateUserAccountWithoutPasswordView.as_view()),
    url(r'^api/user/enroll$', UserEnrollView.as_view()),
]
