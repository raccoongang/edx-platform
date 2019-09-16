from uuid import uuid4

from django.contrib.auth.models import User
from rest_framework import serializers
from social_django.models import UserSocialAuth

from openedx.core.djangoapps.user_api.accounts import (
    EMAIL_CONFLICT_MSG,
    USERNAME_CONFLICT_MSG,
)
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.user_api.accounts.api import (
    get_email_validation_error,
    get_username_validation_error,
)
from ucdc_edx_api.api.exceptions import ResourceConflicts


class UserRegisterSerializer(serializers.ModelSerializer):
    auth_uid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "auth_uid"]

    @staticmethod
    def get_auth_uid(obj):
        qs = UserSocialAuth.objects.filter(user_id=obj.id)
        if qs.count() == 1:
            return qs.first().uid

    @staticmethod
    def validate_email(value):
        validation_status = get_email_validation_error(value)
        if validation_status:
            raise serializers.ValidationError(validation_status)
        return value

    @staticmethod
    def validate_username(value):
        validation_status = get_username_validation_error(value)
        if validation_status:
            raise serializers.ValidationError(validation_status)

        return value

    def validate(self, data):
        _email = data.get("email")
        _username = data.get("username")

        conflicts = check_account_exists(email=_email, username=_username)
        if conflicts:
            conflict_messages = {
                "email": EMAIL_CONFLICT_MSG.format(email_address=_email),
                "username": USERNAME_CONFLICT_MSG.format(username=_username),
            }
            errors = {
                field: [{"user_message": conflict_messages[field]}]
                for field in conflicts
            }
            raise ResourceConflicts(errors)

        return data

    def create(self, validated_data):
        user_obj = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=uuid4().hex,
        )

        return user_obj


class UserSocialAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ["provider", "uid"]

    @staticmethod
    def validate_uid(value):
        if not value or UserSocialAuth.objects.filter(uid=value).exists():
            raise serializers.ValidationError(
                "'uid' %s is unavailable or not unique." % value
            )

        return value

    def create(self, validated_data):
        user_social_auth_obj = UserSocialAuth.objects.create(
            user=validated_data["user"],
            provider=validated_data["provider"],
            uid=validated_data["uid"],
        )
        user_social_auth_obj.save()

        return user_social_auth_obj
