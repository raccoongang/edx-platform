import django_filters
from django_filters import rest_framework as filters
from lms.djangoapps.grades.models import PersistentCourseGrade


class CourseGradesFilter(filters.FilterSet):
    # in URL: ?passed_timestamp_gte=2019-01-02
    passed_timestamp_gte = django_filters.DateTimeFilter(name="passed_timestamp", lookup_expr='gte')

    class Meta:
        model = PersistentCourseGrade
        fields = ('course_id', 'user_id', 'percent_grade', 'letter_grade', 'passed_timestamp', 'passed_timestamp_gte')
