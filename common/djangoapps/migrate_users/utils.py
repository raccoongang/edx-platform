"""
Utils for save data to database.
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.serializers import ValidationError
from social_django.models import UserSocialAuth

from courseware.models import StudentModule, StudentModuleHistory
from migrate_users import error as er
from migrate_users import serializers
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.user_api.models import UserPreference
from student.models import CourseEnrollment, LanguageProficiency, UserProfile


def save_user_information(data_dict):
    """
    Save user information.

    Create new User object and UserProfile object.
    :param data_dict: Dictionary with User information.
    :return: User instance or raise one of: UserAlreadyExistsError, ValueIsMustBeDictionaryError, ValidationUserError.
    """
    if not isinstance(data_dict, dict):
        raise er.ValueIsMustBeDictionaryError(
            "Variable type is {variable_type}".format(
                variable_type=type(data_dict)
            )
        )
    if check_account_exists(username=data_dict.get('username'), email=data_dict.get('email')):
        raise er.UserAlreadyExistsError(
            "Params: user id (remote db)={id} username={username} email={email}".format(
                id=data_dict.get('id'),
                username=data_dict.get('username'),
                email=data_dict.get('email')
            )
        )
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
    return user


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


def save_course_enrollment(course_enrollment_list, user_object):
    """
    Save course enrolment.

    :param course_enrollment_list: List of dictionaries with course enrolments of user.
    :param user_object: User instance.
    """

    if not isinstance(course_enrollment_list, (list, tuple)):
        raise er.ValueIsMustBeListOrTupleError(
            "Variable type is {variable_type}".format(
                variable_type=type(course_enrollment_list)
            )
        )
    if not isinstance(user_object, User):
        raise er.ValueIsMustBeUserTypeError()

    try:
        with transaction.atomic():
            for course_enrollment in course_enrollment_list:
                serializers.CourseEnrollmentSerializer().run_validation(course_enrollment)
                CourseEnrollment.objects.create(
                    user=user_object,
                    course_id=course_enrollment.get('course_id'),
                    created=course_enrollment.get('created'),
                    is_active=course_enrollment.get('is_active'),
                    mode=course_enrollment.get('mode')
                )
    except ValidationError as e:
        raise er.ValidationCourseEnrollmentError(value=str(e))


def save_student_module(student_module_list, user_object):
    """
    Save student's modules.

    :param student_module_list: List of dictionaries with student's module information.
    :param user_object: User instance.
    :return: Dictionary where: key is remote student module id, value is StudentModule instance.
    """
    if not isinstance(student_module_list, (list, tuple)):
        raise er.ValueIsMustBeListOrTupleError(
            "Variable type is {variable_type}".format(
                variable_type=type(student_module_list)
            )
        )
    if not isinstance(user_object, User):
        raise er.ValueIsMustBeUserTypeError()

    try:
        with transaction.atomic():
            id_to_objs_dict = {}
            for student_module in student_module_list:
                student_module['module_state_key'] = student_module.get('module_id')
                serializers.StudentModuleSerializer().run_validation(student_module)
                new_student_module = StudentModule.objects.create(
                    module_type=student_module.get('module_type'),
                    module_state_key=student_module.get('module_id'),
                    course_id=student_module.get('course_id'),
                    state=student_module.get('state'),
                    grade=student_module.get('grade'),
                    max_grade=student_module.get('max_grade'),
                    done=student_module.get('done'),
                    created=student_module.get('created'),
                    modified=student_module.get('modified'),
                    student=user_object
                )
                id_to_objs_dict[str(student_module['id'])] = new_student_module
            return id_to_objs_dict
    except ValidationError as e:
        raise er.ValidationStudentModuleError(str(e))


def save_student_module_history(student_module_history_list, student_module_dict):
    """
    Save student's module history.

    :param student_module_history_list: List of dictionaries with student's module history.
    :param student_module_dict: Dictionary where: key is remote student module id, value is StudentModule instance.
    """
    if type(student_module_history_list) not in [list, tuple]:
        raise er.ValueIsMustBeListOrTupleError(
            "Variable type is {variable_type}".format(
                variable_type=type(student_module_history_list)
            )
        )
    if not isinstance(student_module_dict, dict):
        raise er.ValueIsMustBeDictionaryError(
            "Variable type is {variable_type}".format(
                variable_type=type(student_module_dict)
            )
        )
    try:
        with transaction.atomic():
            for student_module_history in student_module_history_list:
                serializers.StudentModuleHistorySerializer().run_validation(student_module_history)
                student_module_id = student_module_history.get('student_module_id')
                if student_module_id and not isinstance(student_module_dict.get(str(student_module_id)), StudentModule):
                    raise er.DictMustContainsStudentModuleInstanceError
                StudentModuleHistory.objects.create(
                    version=student_module_history.get('version'),
                    created=student_module_history.get('created'),
                    state=student_module_history.get('state'),
                    grade=student_module_history.get('grade'),
                    max_grade=student_module_history.get('max_grade'),
                    student_module=student_module_dict.get(str(student_module_history.get('student_module_id')))
                )
    except ValidationError as e:
        raise er.ValidationStudentModuleHistoryError(str(e))
