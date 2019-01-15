from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^web_science.css$', TemplateView.as_view(
        template_name='web_science/web_science.css.html',
        content_type='text/css',
    ), name='web_science.css'),
]
