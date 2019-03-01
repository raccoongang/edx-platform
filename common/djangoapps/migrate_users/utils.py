"""
Utils for save data to database.
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.serializers import ValidationError
from social_django.models import UserSocialAuth

from migrate_users import error as er
from migrate_users import serializers
from openedx.core.djangoapps.user_api.models import UserPreference
from student.models import CourseEnrollment, LanguageProficiency, UserProfile


def save_user_information(data_dict):
    """
    Save user information.

    Create new User object and UserProfile object. Return existing user if emails are equal.
    If user is created the function returns True as the second tuple value.
    The method retuns the False value like second params in another way.
    :param data_dict: Dictionary with User information.
    :return: tuple of two values: the first is User instance and Boolean value or raise one of: UserAlreadyExistsError,
    ValueIsMustBeDictionaryError, ValidationUserError; and the second: boolean is_user_created flag.
    
    """
    if not isinstance(data_dict, dict):
        raise er.ValueIsMustBeDictionaryError(
            "Variable type is {variable_type}".format(
                variable_type=type(data_dict)
            )
        )

    user_query_set = User.objects.filter(email=data_dict.get('email'))
    if user_query_set.exists():
        return user_query_set.first(), False

    User.objects.filter(username=data_dict.get('username')).exists()

    # The temporary variable for creating the unique username
    temp_username = data_dict.get('username')
    # The 'index' variable is used as suffix for unique username. Example: username1
    index = 1
    # The loop to achive uniqueness of the temp_username.
    # The temp_username suffix is increasing until uniqueness isn't gained.
    while User.objects.filter(username=temp_username).exists():
        temp_username = "{username}{index}".format(username=data_dict.get('username'), index=str(index))
        index += 1

    data_dict['username'] = temp_username

    try:
        user_validation = serializers.UserSerializer()
        user_validation.run_validation(data_dict)
        user_profile_validation = serializers.ProfileSerializer()
        user_profile_validation.run_validation(data_dict)
    except ValidationError:
        raise er.ValidationUserError(
            "username = {username}, email = {email}".format(
                username=data_dict.get('username'),
                email=data_dict.get('email')
            )
        )

    user = User.objects.create(
        username=data_dict.get('username'),
        email=data_dict.get('email'),
        password=data_dict.get('password'),
        last_login=data_dict.get('last_login'),
        is_superuser=data_dict.get('is_superuser'),
        first_name=data_dict.get('first_name'),
        last_name=data_dict.get('last_name'),
        is_staff=data_dict.get('is_staff'),
        is_active=data_dict.get('is_active'),
        date_joined=data_dict.get('date_joined'),
    )

    UserProfile.objects.create(
        user=user,
        name=data_dict.get("name"),
        meta=data_dict.get("meta"),
        courseware=data_dict.get("courseware"),
        language=data_dict.get("language"),
        location=data_dict.get("location"),
        year_of_birth=data_dict.get("year_of_birth"),
        gender=data_dict.get("gender"),
        level_of_education=data_dict.get("level_of_education"),
        mailing_address=data_dict.get("mailing_address"),
        city=data_dict.get("city"),
        country=data_dict.get("country"),
        goals=data_dict.get("goals"),
        allow_certificate=data_dict.get("allow_certificate"),
        bio=data_dict.get("bio"),
        profile_image_uploaded_at=data_dict.get("profile_image_uploaded_at"),
    )
    return user, True


def save_user_social_auth(social_auth_date, user_object):
    """
    Save user social auth.

    :param social_auth_date: Dictionary with information for UserSocialAuth.
    :param user_object: User instance.
    :return: UserSocialAuth instance.
    """
    if not isinstance(social_auth_date, dict):
        raise er.ValueIsMustBeDictionaryError(
            "Variable type is {variable_type}".format(
                variable_type=type(social_auth_date)
            )
        )
    if not isinstance(user_object, User):
        raise er.ValueIsMustBeUserTypeError()
    try:
        user_social_auth_validation = serializers.UserSocialAuthSerializer()
        user_social_auth_validation.run_validation(social_auth_date)
    except ValidationError as e:
        raise er.ValidationUserSocialAuthError(
            str(e),
            "username = {username}, email = {email}".format(
                username=user_object.username,
                email=user_object.email
            )
        )
    return UserSocialAuth.objects.create(
        provider=social_auth_date.get('provider'),
        uid=social_auth_date.get('uid'),
        extra_data=social_auth_date.get('extra_data'),
        user=user_object
    )


def save_user_preference(user_preferences_list, user_object):
    """
    Save user Preferences.

    :param user_preferences_list: List (Tuple) of Dictionaries with User preferences.
    :param user_object: User instance.
    """
    if not isinstance(user_preferences_list, (list, tuple)):
        raise er.ValueIsMustBeListOrTupleError(
            "Variable type is {variable_type}".format(
                variable_type=type(user_preferences_list)
            )
        )
    if not isinstance(user_object, User):
        raise er.ValueIsMustBeUserTypeError()

    try:
        with transaction.atomic():
            for user_preference in user_preferences_list:
                serializers.UserPreferenceSerializer().run_validation(user_preference)
                UserPreference.objects.create(
                    key=user_preference.get('key'),
                    value=user_preference.get('value'),
                    user=user_object
                )
    except ValidationError as e:
        raise er.ValidationUserPreferenceError(str(e))


def save_student_language_proficiency(student_language_proficiency_code, user_profile_object):
    """
    Save studen Language Proficiency.

    :param student_language_proficiency_code: language code.
    :param user_profile_object: UserProfile instance.
    :return: LanguageProficiency instance.
    """

    if not isinstance(user_profile_object, UserProfile):
        raise er.ValueIsMustBeUserProfileTypeError
    try:
        serializers.LanguageProficiencySerializer().run_validation({"code": student_language_proficiency_code})
    except ValidationError as e:
        raise er.ValidationLanguageProficiencyError(str(e))
    return LanguageProficiency.objects.create(
        user_profile=user_profile_object,
        code=student_language_proficiency_code
    )
