"""
Serializer for validate data.
"""
from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer
from social_django.models import UserSocialAuth

from courseware.models import StudentModule, StudentModuleHistory
from openedx.core.djangoapps.user_api.models import UserPreference
from openedx.core.djangoapps.user_api.serializers import ReadOnlyFieldsSerializerMixin
from student.models import CourseEnrollment, LanguageProficiency, UserProfile


class UserSerializer(HyperlinkedModelSerializer):
    """
    Class that serializes the information of User model.
    """

    class Meta(object):
        model = User


class ProfileSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of UserProfile model.
    """

    class Meta(object):
        model = UserProfile
        exclude = ('user',)
        read_only_fields = ('user', 'language_proficiencies')
        explicit_read_only_fields = tuple()


class UserSocialAuthSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of UserSocialAuth model.
    """

    class Meta(object):
        model = UserSocialAuth
        exclude = ('user',)
        read_only_fields = ('user',)
        explicit_read_only_fields = tuple()


class UserPreferenceSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of UserPreference model.
    """

    class Meta(object):
        model = UserPreference
        fields = ('key', 'value')
        read_only_fields = ('user',)
        explicit_read_only_fields = tuple()


class LanguageProficiencySerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of LanguageProficienc model.
    """

    class Meta(object):
        model = LanguageProficiency
        exclude = ('user_profile',)
        read_only_fields = ('user_profile',)
        explicit_read_only_fields = tuple()


class CourseEnrollmentSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of CourseEnrollment model.
    """

    class Meta(object):
        model = CourseEnrollment
        exclude = ('user',)
        read_only_fields = ('user',)
        explicit_read_only_fields = tuple()


class StudentModuleSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of StudentModule model.
    """

    class Meta(object):
        model = StudentModule
        exclude = ('student',)
        read_only_fields = ('student',)
        explicit_read_only_fields = tuple()


class StudentModuleHistorySerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of StudentModuleHistory model.
    """

    class Meta(object):
        model = StudentModuleHistory
        exclude = ('student_module',)
        read_only_fields = ('student_module',)
        explicit_read_only_fields = tuple()
