""" Grades API URLs. """
from django.conf import settings
from django.conf.urls import (
    patterns,
    url,
)

from lms.djangoapps.grades.api import views
from lms.djangoapps.grades.api.v1 import views as views_v1

urlpatterns = patterns(
    '',
    url(
        r'^v0/course_grade/{course_id}/users/$'.format(
            course_id=settings.COURSE_ID_PATTERN,
        ),
        views.UserGradeView.as_view(), name='user_grade_detail'
    ),
    url(
        r'^v0/courses/{course_id}/policy/$'.format(
            course_id=settings.COURSE_ID_PATTERN,
        ),
        views.CourseGradingPolicy.as_view(), name='course_grading_policy'
    ),
    url(
        r'^v1/course_grade/{course_id}/users/$'.format(
            course_id=settings.COURSE_ID_PATTERN,
        ),
        views_v1.UserGradeView.as_view(), name='user_grade_detail'
    ),
    url(
        r'^v1/courses/{course_id}/policy/$'.format(
            course_id=settings.COURSE_ID_PATTERN,
        ),
        views_v1.CourseGradingPolicy.as_view(), name='course_grading_policy'
    ),
)
