from django.conf.urls import patterns, url


urlpatterns = patterns(
    url(r'^enroll', StudentEnrollment.as_view()),
)