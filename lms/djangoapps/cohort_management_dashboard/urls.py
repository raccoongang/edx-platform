"""
Defines the URL routes for this app.
"""
from django.conf.urls import url

from openedx.core.djangoapps.course_groups.views import users_in_cohort
from . import views

app_name = u'lms.djangoapps.cohort_management_dashboard'
urlpatterns = [
    url(r'^dashboard/(?P<cohort_id>\d+)$', views.DashboardIndex.as_view(), name='dashboard_with_cohort'),
    url(r'^dashboard', views.DashboardIndex.as_view(), {'cohort_id': None}, name='dashboard'),
    # Note(yura.braiko@raccongang.com) for some reason rout for all_user_list in edx-platform/lms/urls.py doesn't work.
    url(
        r'^cohort_user_list/(?P<cohort_id>[0-9]+)',
        lambda request, course_id, cohort_id: users_in_cohort(request, course_id, cohort_id),
        name='all_user_list'
    ),
]
