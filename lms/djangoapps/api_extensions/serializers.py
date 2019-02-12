from rest_framework import serializers
from lms.djangoapps.grades.models import PersistentCourseGrade
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class PersistentCourseGradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersistentCourseGrade
        fields = ('course_id', 'user_id', 'percent_grade', 'letter_grade', 'passed_timestamp', 'course_title')

    course_title = serializers.SerializerMethodField()

    def get_course_title(self, obj):
        return CourseOverview.objects.get(id=obj.course_id).display_name  # or  display_name_with_default

