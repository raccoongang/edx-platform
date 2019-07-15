from rest_framework import serializers

from .models import City, School, InstructorProfile


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
