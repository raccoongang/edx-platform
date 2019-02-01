from django.conf.urls import url
from django.views.generic import TemplateView
from django.conf import settings

from web_science.views import WebScienceUnitLogView

urlpatterns = [
    url(r'^web_science.css$', TemplateView.as_view(
        template_name='web_science/web_science.css.html',
        content_type='text/css',
    ), name='web_science.css'),
    url(
        r'^log/{usage_key}?$'.format(usage_key=settings.USAGE_ID_PATTERN),
        WebScienceUnitLogView.as_view(),
        name='web_science_unit_log'
    ),
]
