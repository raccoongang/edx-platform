from rest_framework import serializers
from lms.djangoapps.grades.models import PersistentCourseGrade
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from django.contrib.auth import get_user_model
User = get_user_model()


class PersistentCourseGradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersistentCourseGrade
        fields = ('course_id', 'user_id', 'percent_grade', 'letter_grade', 'passed_timestamp', 'course_title', 'username', 'email')

    course_title = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_course_title(self, obj):
        return CourseOverview.objects.get(id=obj.course_id).display_name

    def get_username(self, obj):
        return User.objects.get(id=obj.user_id).username

    def get_email(self, obj):
        return User.objects.get(id=obj.user_id).email
