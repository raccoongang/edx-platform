from opaque_keys.edx.keys import CourseKey
from rest_framework import serializers

from .models import City, School, InstructorProfile, VideoLesson, Question



class InstructorProfileSerilizer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.profile.name or obj.user.username

    class Meta:
        model = InstructorProfile
        fields = ('id', 'username')
        read_only_fields = ('username',)


class SchoolSerilizer(serializers.ModelSerializer):
    instructors = serializers.SerializerMethodField()

    def get_instructors(self, obj):
        return InstructorProfileSerilizer(
            obj.instructorprofile_set.filter(user__is_staff=True, user__is_active=True),
            many=True
        ).data

    class Meta:
        model = School
        fields = ('id', 'name', 'instructors')
        read_only_fields = ('name', 'instructors')


class SingleSchoolSerilizer(serializers.ModelSerializer):
    """
    Return only School fields
    """

    class Meta:
        model = School
        fields = ('id', 'name')
        read_only_fields = ('name',)


class CitySerializer(serializers.ModelSerializer):
    schools = serializers.SerializerMethodField()

    def get_schools(self, obj):
        return SingleSchoolSerilizer(obj.schools.all(), many=True).data

    class Meta:
        model = City
        fields = ('id', 'name', 'schools')
        read_only_fields = ('name', 'schools')


class SingleCitySerializer(serializers.ModelSerializer):
    """
    Return only city fields
    """
    class Meta:
        model = City
        fields = ('id', 'name')
        read_only_fields = ('name',)


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('question_id', 'attempt_count')


class VideoLessonSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = VideoLesson
        fields = ('user', 'course', 'video_id', 'questions')

    def create(self, validated_data):
        questions_answered = validated_data.pop('questions')
        course = CourseKey.from_string(validated_data.pop('course'))
        video_lesson, create = VideoLesson.objects.get_or_create(course=course, **validated_data)
        for question_data in questions_answered:
            question_id = question_data.pop('question_id')
            question = Question.objects.update_or_create(
                video_lesson=video_lesson,
                question_id=question_id,
                defaults=question_data,
            )
        return video_lesson
