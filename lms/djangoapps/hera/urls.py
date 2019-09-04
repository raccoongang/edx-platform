"""
URL definitions for hera app.
"""

from django.conf.urls import url

from hera import views

urlpatterns = [
    url(r'^onboarding/', views.OnboardingPagesView.as_view(), name='onboarding')
]
