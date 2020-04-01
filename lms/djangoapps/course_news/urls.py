"""
Course news tab urls.
"""
from django.conf.urls import url, patterns

from .views import CourseNewsFragmentView, course_news

urlpatterns = patterns(
    'course_news.views',

    url(
        r'course_news_fragment_view$',
        CourseNewsFragmentView.as_view(),
        name='course_news_fragment_view'
    ),
    url(r'', 'course_news', name='course_news_view'),
)
