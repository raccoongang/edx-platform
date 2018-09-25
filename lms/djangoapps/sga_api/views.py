"""
APIView endpoints for creating and bulk enrolling users
"""
import logging
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, validate_slug
from django_countries import countries
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from enrollment.views import ApiKeyPermissionMixIn, EnrollmentCrossDomainSessionAuth, EnrollmentUserThrottle
from lms.djangoapps.instructor.enrollment import enroll_email, get_email_params, get_user_email_language, unenroll_email
from lms.djangoapps.instructor.views.tools import get_student_from_identifier
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.user_api.preferences.api import update_user_preferences
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from student.forms import PasswordResetFormNoActive
from student.models import UserProfile
from student.views import create_account_with_params
from xmodule.modulestore.django import modulestore

log = logging.getLogger(__name__)


class CreateUserAccountWithoutPasswordView(APIView):
    """
    Create user account without password
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    def post(self, request):
        """
        Create user account without password

        Creates a user using mail, login and also name and surname.
        Sets a random password and sends a user a message to change it.
        """
        data = request.data
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"
        email = request.data.get('email')
        username = request.data.get('username')
        # countries.by_name return country code or '' for else cases
        country = countries.by_name(request.data.get('country', ''))
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        language = request.data.get('language')
        if not username:
            error_msg = "username is required parameter."
        elif not email:
            error_msg =  "email is required parameter."
        elif not country:
            error_msg = (
                "Country is wrong or absent: {country}. For checking: Visit https://www.iso.org/obp . "
                "Click the Country Codes radio option and click the search button."
            ).format(country=request.data.get('country', ''))
        else:
            error_msg = None

        if error_msg:
            return Response(
                data={"error_message": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_slug(username)
        except ValidationError:
            return Response(
                data={
                    "error_message": "Enter a valid 'username' consisting of letters, numbers, underscores or hyphens."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data['name'] = "{} {}".format(first_name, last_name).strip() if first_name or last_name else username

        if check_account_exists(username=username, email=email):
            return Response(data={"error_message": "User already exists"}, status=status.HTTP_409_CONFLICT)

        try:
            data['password'] = uuid4().hex
            data['country'] = country
            user = create_account_with_params(request, data)
            user.is_active = True
            user.save()
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.phone = request.data.get('phone', '')
            user_profile.save()
            # dict to setup language
            update = {u'pref-lang': language}
            # setup language for user
            update_user_preferences(user, update, username)
            self.send_activation_email(request)
        except ValidationError:
            return Response(data={"error_message": "Wrong email format"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)

    @staticmethod
    def send_activation_email(request):
        """
        Send activation email with reset password.
        """
        form = PasswordResetFormNoActive(request.data)
        if form.is_valid():
            form.save(
                use_https=request.is_secure(),
                from_email=configuration_helpers.get_value(
                    'email_from_address', settings.DEFAULT_FROM_EMAIL
                ),
                request=request,
                subject_template_name='sga_api/set_password_subject.txt',
                email_template_name='sga_api/set_password_email.html'
            )


class BulkEnrollView(APIView, ApiKeyPermissionMixIn):
    """
    API endpoint for bulk enrolling/unenrolling users on the courses.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)

    def post(self, request):
        """
        Bulk enrolling/unenrolling users on the courses.

        Enroll or unenroll users on the courses.
        """
        data = request.data
        users = data.get('users')
        courses = data.get('courses')
        action = data.get('action', 'enroll')
        email_students = data.get('email_students', False)
        auto_enroll = data.get('auto_enroll', False)

        if action not in ['enroll', 'unenroll']:
            error_msg = "action must be enroll or unenroll"
        elif not isinstance(courses, (list, tuple)):
            error_msg = "courses must be a list of courses id "
        elif not isinstance(users, (list, tuple)):
            error_msg =  "users must be a list of identifiers(username or email)"
        else:
            error_msg = None

        if error_msg:
            return Response(
                data={"error_message": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = self._enroll_unenrol_users_for_courses(
                courses, users, request, action, email_students, auto_enroll
            )

            return Response(
                data={
                    'action': action,
                    'courses': result,
                    'email_students':email_students,
                    'auto_enroll': auto_enroll,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            log.error(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _enroll_unenrol_users_for_courses(
        self, list_of_courses_id, list_of_users_email,
        request, action='enroll', email_students=False, auto_enroll=False
    ):
        courses = {}
        for course_id in list_of_courses_id:
            results = self._enroll_unenrol_users_for_course(
                course_id, list_of_users_email, request,
                action, email_students, auto_enroll
            )
            courses[course_id] = self._make_result_dict_for_course(
                 results, action, auto_enroll
            )
        return courses

    def _enroll_unenrol_users_for_course(
            self, course_id, list_of_users_email, request,
            action='enroll', email_students=False, auto_enroll=False
    ):
        result_list = []
        for users_email in list_of_users_email:
    
            try:
                user = get_student_from_identifier(users_email)
                email = user.email
                language = get_user_email_language(user)
            except User.DoesNotExist:
                if auto_enroll and action == 'enroll':
                    email = users_email
                    language = None
                else:
                    result_list.append(
                        self._make_result_dict_for_identifier(
                            users_email=users_email,
                            error='User with {} users_email has not valid email'.format(users_email),
                            after={}, before={}
                        )
                    )
                    continue
            try:
                course_id_obj = SlashSeparatedCourseKey.from_deprecated_string(course_id)
                course = modulestore().get_course(course_id_obj)
                if not course:
                    raise InvalidKeyError('course', 'Wrong course_id')
                    
                if email_students:
                    email_params = get_email_params(course, auto_enroll, secure=request.is_secure())
                else:
                    email_params = None
                validate_email(email)
                if action == 'enroll':
                    before, after, _ = enroll_email(
                        course_id_obj, email, auto_enroll, email_students, email_params, language=language
                    )
                else:
                    before, after = unenroll_email(
                        course_id_obj, email, email_students, email_params, language=language
                    )

                result_list.append(
                    self._make_result_dict_for_identifier(
                        users_email=users_email, after=after.to_dict(), before=before.to_dict(),
                    )
                )
            except ValidationError:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        users_email=users_email,
                        error='User with {} users_email has not valid email'.format(users_email),
                        after={}, before={}
                    )
                )
            except InvalidKeyError:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        users_email=users_email,
                        error='Wrong course_id: {}. Course does not exist'.format(course_id),
                        after={}, before={}
                    )
                )
            except Exception as exc:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        users_email=users_email, error='Problem winth {}ing user. Error: {}'.format(action, exc),
                        after={}, before={}
                    )
                )
                log.error(exc)
        return result_list

    @staticmethod
    def _make_result_dict_for_identifier(users_email, after, before, error=''):
        return {
            'identifier': users_email,
            'after': after,
            'before': before,
            'error': error,
        }

    @staticmethod
    def _make_result_dict_for_course(results_list, action='enroll', auto_enroll=False):
        return {
            "action": action,
            'results': results_list,
            'auto_enroll': auto_enroll,
        }
