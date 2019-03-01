"""
Serializer for validate data.
"""
from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer
from social_django.models import UserSocialAuth

from openedx.core.djangoapps.user_api.models import UserPreference
from openedx.core.djangoapps.user_api.serializers import ReadOnlyFieldsSerializerMixin
from student.models import CourseEnrollment, LanguageProficiency, UserProfile


class UserSerializer(HyperlinkedModelSerializer):
    """
    Class that serializes the information of User model.
    """

    class Meta(object):
        model = User
        fields = '__all__'


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
