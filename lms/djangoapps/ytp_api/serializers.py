# coding=utf-8
"""
Serializer for validate data.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.serializers import HyperlinkedModelSerializer

from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.user_api.serializers import ReadOnlyFieldsSerializerMixin
from student.models import CourseEnrollment, LanguageProficiency, UserProfile


class UserSerializer(HyperlinkedModelSerializer):
    """
    Class that serializes the information of User model.

    Update and validate User information.
    """

    class Meta(object):
        model = User
        read_only_fields = ('password', 'username')

    def update(self, instance, data):
        """
        Update User instance for date dictionary.

        Method can update User instance if data is correct.
        :param instance:
        :param data:
        :return:
        """
        if not isinstance(instance, User):
            raise ValidationError("The instance must be the User type.")
        username = data.get("username")
        if isinstance(data, dict) and username and (instance.username != username):
            instance.username = self._validate_username(data)
        email = data.get("email")
        if isinstance(data, dict) and email and (instance.email != email):
            self._check_email_unique(data.get("email"))

        validated_data = self.run_validation(data)
        for field_name in validated_data:
            default = getattr(instance, field_name)
            field_value = validated_data.get(field_name, default)
            setattr(instance, field_name, field_value)
        instance.save()
        return instance

    @staticmethod
    def _validate_username(data):
        """
        Validate username filed in User object.

        :param data: Dictionary with key username
        :return: The username value
        """
        validate_data = UserUsernameSerializer().run_validation(data)
        return validate_data.get("username")

    @staticmethod
    def _check_email_unique(email):
        if check_account_exists(email=email):
            raise ValidationError("User already exists with this email")


class UserUsernameSerializer(HyperlinkedModelSerializer):
    """
    Class that serializes the information of User model.

    Validate user's username.
    """

    class Meta(object):
        model = User
        fields = ('username',)


class ProfileSerializer(HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the information of UserProfile model.

    Update and validate User information.
    """

    class Meta(object):
        model = UserProfile
        exclude = ('user',)
        read_only_fields = ('user', 'language_proficiencies')
        explicit_read_only_fields = tuple()

    def update(self, instance, data):
        if not isinstance(instance, UserProfile):
            raise ValidationError("The instance must be the UserProfile type.")

        validated_data = self.run_validation(data)
        for field_name in validated_data:
            default = getattr(instance, field_name)
            field_value = validated_data.get(field_name, default)
            setattr(instance, field_name,field_value)
        instance.save()
        return instance
