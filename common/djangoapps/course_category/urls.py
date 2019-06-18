from django.conf.urls import patterns, url

from course_category import views

urlpatterns = patterns(
    '',
    # pylint seems to dislike as_view() calls because it's a `classonlymethod` instead of `classmethod`, so we disable the warning
    url(r'^$', views.CourseCategoryView.as_view(), name='course_category_list'),
    url(r'^(?P<slug>[-\w]+)/$', views.CategoryCoursesListView.as_view(), name='courses_list_for_category'),
) 
