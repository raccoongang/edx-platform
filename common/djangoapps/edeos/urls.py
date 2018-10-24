from django.conf import settings
from django.conf.urls import patterns, url

# from .views import update_wallet


urlpatterns = patterns('edeos.views',
    url(r'^update-wallet/', 'update_wallet', name="update"),
    url(r'^generate-wallet/', 'generate_wallet', name="generate-wallet"),
)
