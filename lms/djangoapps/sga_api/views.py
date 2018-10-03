"""
APIView endpoints for creating and bulk enrolling users
"""
import logging
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
from student.views import create_account_with_params
from xmodule.modulestore.django import modulestore

log = logging.getLogger(__name__)


class CreateUserAccountWithoutPasswordView(APIView):
    """
    Create user account without password.
    """
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (ApiKeyHeaderPermission,)
    
    _error_dict = {
        "username": "Username is required parameter.",
        "email": "Email is required parameter.",
        "country": (
            "Country is incorrect or missed: {value}. For checking: Visit https://www.iso.org/obp . "
            "Click the Country Codes radio option and click the search button."
        ),
        "language": "Language is incorrect or missed: {value}. It must be:  pt (Portuguese) or en (English)"
    }

    def post(self, request):
        """
        Create a user by email, login, country, and language.

        Create user account and send activation email to the user.
        """
        data = request.data
        data['honor_code'] = "True"
        data['terms_of_service'] = "True"
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        try:
            email = self._check_available_required_params(request.data.get('email'), "email")
            username = self._check_available_required_params(request.data.get('username'), "username")
            # NOTE(AndreyLykhoman): countries.by_name function returns country code or '' if country isn't found.
            country = self._check_available_required_params(countries.by_name(request.data.get('country')), "country")
            language = self._check_available_required_params(request.data.get('language'), 'language', ['en', 'pt-br'])
            if check_account_exists(username=username, email=email):
                return Response(data={"error_message": "User already exists"}, status=status.HTTP_409_CONFLICT)

            data['name'] = "{} {}".format(first_name, last_name).strip() if first_name or last_name else username
            data['password'] = uuid4().hex
            data['country'] = country
            user = create_account_with_params(request, data)
            user.is_active = True
            user.first_name = first_name
            user.last_name = last_name
            user.profile.phone = request.data.get('phone')
            user.profile.save()
            user.save()
            # setup language for user
            update_user_preferences(user, {u'pref-lang': language})
            self.send_activation_email(request)
        except ValueError as e:
            log.error(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(data={"error_message": e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)
    
    def _check_available_required_params(self, parameter, parameter_name, values_list=None):
        """
        Raise ValueError if param not available or not in list. Also return param.
        
        :param parameter: object
        :param parameter_name: string. Parameter's name
        :param values_list: List of values
        
        :return: parameter
        """
        if not parameter or (values_list and isinstance(values_list, list) and parameter not in values_list):
            raise ValueError(self._error_dict[parameter_name].format(value=parameter))
        return parameter
        

    @staticmethod
    def send_activation_email(request):
        """
        Send email to activation and reset password.
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
        if action not in ['enroll', 'unenroll']:
            return Response(
                data={"error_message": "Action must be enroll or unenroll"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(email_students, bool):
            return Response(
                data={"error_message": "Email_students must be boolean value: true or false"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            courses = self._make_list_from_str_or_tuple(courses, "Courses")
            users = self._make_list_from_str_or_tuple(users, "Users")
            result = self._enroll_unenroll_users_for_courses(courses, users, request, action, email_students)
            return Response(
                data={
                    'action': action, 'courses': result, 'email_students':email_students,
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            log.error(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _enroll_unenroll_users_for_courses(
        self, list_of_courses_id, list_of_users_email, request, action='enroll', email_students=False,
    ):
        """
        Enroll/Unenroll users for courses.
        
        :param list_of_courses_id:  list of courses id/
        :param list_of_users_email: list of user's email
        :param request: request for Api endpoint
        :param action:  string 'enroll' or 'unenroll'. 'enroll' is default value.
        :param email_students: boolean. send email after enroll. False is default value.
        :return: dictionary with enroll/unenroll results
        """
        courses = {}
        for course_id in list_of_courses_id:
            results = self._enroll_unenroll_users_for_course(
                course_id, list_of_users_email, request, action, email_students
            )
            courses[course_id] = self._make_result_dict_for_course(results, action)
        return courses

    def _enroll_unenroll_users_for_course(
            self, course_id, list_of_users_email, request, action='enroll', email_students=False
    ):
        """
        Enroll/unenroll users for one course.
        
        :param course_id: Course id. string
        :param list_of_users_email: List of user's email
        :param request: request for Api endpoint
        :param action: string 'enroll' or 'unenroll'. 'enroll' is default value.
        :param email_students: boolean. send email after enroll. False is default value.
        :return:  list of dicts
        """
        result_list = []
        for user_email in list_of_users_email:
            try:
                user = get_student_from_identifier(user_email)
                language = get_user_email_language(user)
                course_id_obj = SlashSeparatedCourseKey.from_deprecated_string(course_id)
                course = modulestore().get_course(course_id_obj)
                if not course:
                    raise InvalidKeyError('course', 'Wrong course_id')
                    
                if email_students:
                    email_params = get_email_params(course, False, secure=request.is_secure())
                else:
                    email_params = None

                if action == 'enroll':
                    before, after, _ = enroll_email(
                        course_id_obj,
                        user_email,
                        email_students=email_students,
                        email_params = email_params,
                        language=language
                    )
                else:
                    before, after = unenroll_email(
                        course_id_obj, user_email, email_students, email_params, language
                    )

                result_list.append(
                    self._make_result_dict_for_identifier(
                        user_email, after=after.to_dict(), before=before.to_dict(),
                    )
                )
            except User.DoesNotExist:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        user_email,
                        error='User with {user_email} user_email does not exist'.format(user_email=user_email),
                    )
                )
            except ValidationError:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        user_email,
                        error='User with {user_email} user_email has not valid user_email'.format(user_email=user_email)
                    )
                )
            except InvalidKeyError:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        user_email,
                        error='Wrong course_id: {course_id}. Course does not exist'.format(course_id=course_id)
                    )
                )
            except Exception as exc:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        user_email, error='Problem with {action}ing user. Error: {exc}'.format(action=action, exc=exc)
                    )
                )
                log.error(exc)
        return result_list

    @staticmethod
    def _make_result_dict_for_identifier(user_email, after=None, before=None, error=''):
        """
        Make a dictionary that show result enroll/unenroll for user
        
        :param user_email: string. User email
        :param after: dict with enroll information or empty dict
        :param before: dict with enroll information or empty dict
        :param error: string with error message or empty string
        :return: dict
        """
        return {
            'identifier': user_email,
            'after': after or {},
            'before': before or {},
            'error': error,
        }

    @staticmethod
    def _make_result_dict_for_course(results_list, action='enroll'):
        """
        Make a dictionary that show result enroll/unenroll for all user for one course
        
        :param results_list: list of dict
        :param action: string 'enroll' or 'unenroll'. 'enroll' is default value.
        :return: dict
        """
        return {
            "action": action,
            'results': results_list,
        }
    
    @staticmethod
    def _make_list_from_str_or_tuple(str_or_tuple, name_in_msg = "Variable"):
        """
        Return List or raise ValueError.
        
        If method make list from str or tuple. If value is not list, str or tuple then raise ValueError.
        :params
            str_or_list: list, tuple or string
            name_in_msg: Name variable in error message.
        :return: list or tuple
        
        """
        if isinstance(str_or_tuple, (list, tuple)):
            return str_or_tuple
        elif isinstance(str_or_tuple, str):
            return [str_or_tuple]
        else:
            raise ValueError("{name_in_msg} must be a list.".format(name_in_msg=name_in_msg))
