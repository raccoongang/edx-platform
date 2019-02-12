from django.conf import settings
from django.conf.urls import url
from lms.djangoapps.api_extensions import views

urlpatterns = [
    url(r'^course_grades_filter/{course_id}/$'.format(
            course_id=settings.COURSE_ID_PATTERN,
        ), views.CourseGradesFilterView.as_view({'get': 'list'}))
    ]
