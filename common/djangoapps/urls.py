"""
Urls for Admin Dashboard
"""

from django.conf.urls import url
from admin_dashboard import views
from admin_dashboard import api

urlpatterns = [

    url(r'^$', views.index, name='admin_dashboard'),
    url(r'^add_users', views.add_users, name='add_users'),
    url(r'^create_bulk_users', api.create_bulk_users, name='create_bulk_users'),
]
