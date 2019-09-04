from django.conf.urls import url

from onboarding import views

app_name = 'onboarding'
urlpatterns = [
    url(r'^onboarding/', views.OnboardingPagesView.as_view(), name='onboarding')
]