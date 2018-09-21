import logging
from uuid import uuid4
from django.http import Http404
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from student.views import create_account_with_params
from enrollment.views import EnrollmentCrossDomainSessionAuth, EnrollmentUserThrottle, ApiKeyPermissionMixIn
from django.core.validators import validate_slug, validate_email
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from student.forms import PasswordResetFormNoActive
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.djangoapps.user_api.preferences.api import update_user_preferences
from django_countries import countries
from student.models import UserProfile
from lms.djangoapps.instructor.enrollment import get_email_params, enroll_email, get_user_email_language, unenroll_email
from lms.djangoapps.instructor.views.tools import get_student_from_identifier
from courseware.courses import get_course_by_id

log = logging.getLogger(__name__)


class CreateUserAccountWithoutPasswordView(APIView):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermission,

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
        elif not request.data.get('country', ''):
            error_msg = "country is required parameter."
        elif request.data.get('country', '') and not country:
            # If request has country property but it's wrong
            # and countries.by_name returned ''
            error_msg = "Wrong country: {}. " \
                        "For checking: Visit https://www.iso.org/obp . " \
                        "Click the Country Codes radio " \
                        "option and click the search button.".format(request.data.get('country', ''))
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

        data['name'] =  "{} {}".format(first_name, last_name).strip() if first_name or last_name else username

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
            update = {
                u'pref-lang': language,
            }
            #setup language for user
            update_user_preferences(user, update, username)
            self.send_activation_email(request)
        except ValidationError:
            return Response(data={"error_message": "Wrong email format"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)

    @staticmethod
    def send_activation_email(request):
        form = PasswordResetFormNoActive(request.data)
        if form.is_valid():
            form.save(use_https=request.is_secure(),
                      from_email=configuration_helpers.get_value(
                          'email_from_address', settings.DEFAULT_FROM_EMAIL),
                      request=request,
                      subject_template_name='sga_api/set_password_subject.txt',
                      email_template_name='sga_api/set_password_email.html'
                      )



class BulkEnrollView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = ApiKeyHeaderPermission,

    def post(self, request):
        """
        Enrolling user on the course with the specified mod.
        Create or update enroll user on the course. Can deactivate enroll
        or activate enroll with use 'is_active' param.
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
            error_msg = "courses_id must be a list of courses_id "
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
            result = self.__enroll_unenrol_users_for_courses(
                courses, users, request,
                action, email_students, auto_enroll
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
        except  Exception as e:
            log.error(e.message)
            return Response(
                data={"error_message": e.message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def __enroll_unenrol_users_for_courses(
            self, courses_id, identifiers, request,
            action='enroll', email_students=False, auto_enroll=False
    ):
        courses = {}
        for course_id in courses_id:
            results = self._enroll_unenrol_users_for_course(
                course_id, identifiers, request,
                action, email_students, auto_enroll
            )
            courses[course_id] = self._make_result_dict_for_course(
                 results, action, auto_enroll
            )
        return courses

    def _enroll_unenrol_users_for_course(
            self, course_id, identifiers, request,
            action='enroll', email_students=False, auto_enroll=False
    ):
        result_list = []
        for identifier in identifiers:
            try:
                course_id_obj = SlashSeparatedCourseKey.from_deprecated_string(course_id)
                course = get_course_by_id(course_id_obj)
                if email_students:
                    email_params = get_email_params(course, auto_enroll, secure=request.is_secure())
                else:
                    email_params = None

                try:
                    user = get_student_from_identifier(identifier)
                    email = user.email
                    language = get_user_email_language(user)
                except User.DoesNotExist as e:
                    if auto_enroll and action == 'enroll':
                        email = identifier
                        language = None
                    else:
                        raise e

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
                        identifier=identifier, after=after.to_dict(), before=before.to_dict(),
                    )
                )
            except User.DoesNotExist:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        identifier=identifier,
                        error='User with {} identifier does not exist'.format(identifier)
                    )
                )
            except Http404:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        identifier=identifier,
                        error='Wrong course_id: {}. Course does not exist'.format(course_id)
                    )
                )
            except ValidationError:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        identifier=identifier,
                        error='User with {} identifier has not valid email'.format(identifier)
                    )
                )
            except Exception as exc:
                result_list.append(
                    self._make_result_dict_for_identifier(
                        identifier=identifier,
                        error='Problem winth {}ing user. Error: {}'.format(action, exc)
                    )
                )
                log.error(exc)
        return result_list

    def _make_result_dict_for_identifier(
            self, identifier, after={}, before={}, error=''
    ):
        return {
            'identifier': identifier,
            'after': after,
            'before': before,
            'error': error,
        }

    def _make_result_dict_for_course(self, results_list, action='enroll', auto_enroll=False):
        return {
            "action": action,
            'results': results_list,
            'auto_enroll': auto_enroll,
        }
