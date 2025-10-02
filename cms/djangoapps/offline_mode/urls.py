from django.urls import path

from . import views

app_name = "cms_offline_mode"

urlpatterns = [
    path("generate_offline_archive/<course_id>", views.generate_offline_archive, name="generate_offline_archive"),
]
