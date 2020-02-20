"""
URL definitions for hera app.
"""

from django.conf import settings
from django.conf.urls import url

from hera import views

urlpatterns = [
    url(r'^onboarding/$', views.OnboardingPagesView.as_view(), name='onboarding'),
    url(r'^user_dashboard/$', views.DashboardPageView.as_view(), name='dashboard'),
    #TODO: delete selection_page
    url(r'^courses/{}/course/selection_page/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        views.SelectionPageView.as_view(), name='selection_page'),
    url(r'^register_success/$', views.RegisterSuccessView.as_view(), name="register_success"),
]
