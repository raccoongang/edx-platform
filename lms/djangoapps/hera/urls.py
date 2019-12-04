"""
URL definitions for hera app.
"""

from django.conf.urls import url

from hera import views

urlpatterns = [
    url(r'^onboarding/', views.OnboardingPagesView.as_view(), name='onboarding'),
    url(r'^selection_page/', views.SelectionPageView.as_view(), name='selection_page'),
]
