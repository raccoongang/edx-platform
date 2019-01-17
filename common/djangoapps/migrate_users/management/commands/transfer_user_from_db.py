"""
Manage.py command for migrate users with progress.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from courseware.models import StudentModule
from migrate_users import utils
from migrate_users import error as er
from migrate_users.remote_db_helpers import RemoteDBQuery
from student.models import CourseEnrollment


class Command(BaseCommand):
    """
    Transfer users with progress between databases.
    """

    help = "Transfer users with progress from one database (by connection_name) to default database"

    def add_arguments(self, parser):
        parser.add_argument("connection_name", help="name of database connection to DB with source data")
        parser.add_argument('-c', '--courses', dest='courses_id', nargs='*', default=[], help="Filter for courses id")

    def handle(self, connection_name, courses_id, *args, **options):
        """
        Migrate users with progress in remote DB to current DB.

        :param connection_name: connection name of remote DB in django settings.
        :param courses_id: List of course key. If need filtered by course.
        :return:
        """
        self.stdout.write("connection_name: {connection_name}".format(connection_name=connection_name))
        try:
            # Already created users dictionary: key: remote user id, value: current user id
            count_of_created_users = {}
            # Contain error for crete users: key: remote user id value: error string
            dict_with_error_creating = {}

            # Object for work with remote DB by connection name
            remote_db_query = RemoteDBQuery(connection_name)
            # Get user id list
            if courses_id:
                # if courses_id has some course key for filtering course id
                user_in_courses = remote_db_query.get_users_id_list_from_course_id(courses_id)
                user_id_list = [user['user_id'] for user in user_in_courses]
            else:
                # get all users id un remote DB
                all_users = remote_db_query.get_all_users_id()
                user_id_list = [user['id'] for user in all_users]
            for user_id in user_id_list:
                try:
                    with transaction.atomic():
                        user_info = remote_db_query.get_user_information_by_id(user_id)
                        if not user_info:
                            raise er.UserInformationDoesNotExistsInRemoteDBError(
                                "user id = {}".format(user_id)
                            )
                        # It's here because remote_db_query.get_user_information_by_id always returns a list of dict or
                        # a empty list. But the self._save_user_information method can work with dict and code uses
                        # this variable to get 'userprofile_id'.
                        user_info = user_info[0]
                        # Create User and UserProfile
                        self.stdout.write("Create User and UserProfile")
                        user =  utils.save_user_information(user_info)
                        # Work with UserSocialAuth
                        user_social_auth = remote_db_query.get_user_social_auth_by_id(user_id)
                        if user_social_auth:
                            self.stdout.write("Create UserSocialAuth")
                            utils.save_user_social_auth(user_social_auth[0], user)
                        # Work with UserPreference
                        user_preference = remote_db_query.get_user_preferences_by_user_id(user_id)
                        if user_preference:
                            self.stdout.write("Create UserPreference")
                            utils.save_user_preference(user_preference, user)
                        # Work with LanguageProficiency
                        student_languageproficiency = remote_db_query.get_student_language_proficiency_by_profile_id(
                            user_info['userprofile_id']
                        )
                        if student_languageproficiency:
                            self.stdout.write("Create LanguageProficiency")
                            utils.save_student_language_proficiency(
                                student_languageproficiency[0]['code'], user.profile
                            )
                        # Work with CourseEnrollment
                        course_enrollment = remote_db_query.get_course_enrollments(user_id, courses_id)
                        if course_enrollment:
                            self.stdout.write("Create CourseEnrollment")
                            utils.save_course_enrollment(course_enrollment, user)
                        student_module = remote_db_query.get_student_modules(user_id, courses_id)
                        # Work with StudentModules
                        if student_module:
                            # Save StudentModules
                            self.stdout.write("Create StudentModules")
                            student_module_id_to_obj_dict = utils.save_student_module(student_module, user)
                            # Work with StudentModulesHistory
                            student_module_history = remote_db_query.get_student_module_history(
                                student_module_id_to_obj_dict.keys()
                            )
                            if student_module_history:
                                self.stdout.write("Create StudentModulesHistory")
                                utils.save_student_module_history(
                                    student_module_history, student_module_id_to_obj_dict
                                )
                        self.stdout.write("User created ({id}): {user}, profile: {profile} ".format(
                            id=user.id,
                            user=user,
                            profile=user.profile
                        ))
                        count_of_created_users[str(user_id)] = str(user.id)
                except (
                    er.UserInformationDoesNotExistsInRemoteDBError,
                    er.UserAlreadyExistsError,
                    er.ValidationUserError,
                    er.ValidationUserSocialAuthError,
                    er.ValidationUserPreferenceError,
                    er.ValidationLanguageProficiencyError,
                    er.ValidationCourseEnrollmentError,
                    er.ValidationStudentModuleError,
                    er.ValidationStudentModuleHistoryError
                ) as e:
                    self.stderr.write(str(e))
                    dict_with_error_creating[str(user_id)] = str(e)

            # Test of rebase users and write total information

            self.stdout.write("Total Information:")
            self.stdout.write("__________________")
            # Information about created uses and errors
            self.stdout.write(
                "Created {count_of_users} users out of {count_remote_user_for_rebase} users".format(
                    count_of_users=len(count_of_created_users),
                    count_remote_user_for_rebase=len(user_id_list)
                )
            )
            if count_of_created_users:
                # information about errors
                if dict_with_error_creating:
                    self.stderr.write("Count of errors: {errors}: ".format(errors=len(dict_with_error_creating)))
                    self.stderr.write("_______________")
                    for key, value in dict_with_error_creating.items():
                        self.stderr.write(
                            "Error for User with remote id {remote_id}: {error}".format(
                                remote_id=key,
                                error=value
                            )
                        )
                # Information about course enrolments
                current_course_enrollment_count = CourseEnrollment.objects.filter(
                    user__id__in=count_of_created_users.values()
                ).count()
                remote_course_enrollment_list = remote_db_query.get_course_enrollments_count(
                    count_of_created_users.keys(), courses_id
                )
                if remote_course_enrollment_list:
                    remote_result_dict = remote_course_enrollment_list[0]
                    count = remote_result_dict["count"]
                    if count == current_course_enrollment_count:
                        self.stdout.write("Created All course enrolments for created users")
                    else:
                        self.stderr.write("Created {current} enrollments out of {remote}".format(
                            current=current_course_enrollment_count,
                            remote=count
                        ))
                else:
                    self.stderr.write("Remote DB doesn't has any course enrollments for created users")

                # Information about grades
                current_student_module_count = StudentModule.objects.filter(
                    student__id__in=count_of_created_users.values()
                ).count()
                remote_student_module_list = remote_db_query.get_student_modules_count(
                    count_of_created_users.keys(), courses_id
                )
                if remote_student_module_list:
                    remote_student_dict = remote_student_module_list[0]
                    count = remote_student_dict["count"]
                    if count == current_student_module_count:
                        self.stdout.write("Created All course modules for created users. Grade migrated.")
                    else:
                        self.stderr.write("Created {current} course modules out of {remote}".format(
                            current=current_course_enrollment_count,
                            remote=count
                        ))
                else:
                    self.stderr.write("Remote DB doesn't has any course modules for created users.")

        except er.WrongConnectionNameError as e:
            self.stderr.write(e)
        except (
            er.ValueIsMustBeDictionaryError,
            er.ValueIsMustBeListOrTupleError,
            er.ValueIsMustBeUserTypeError,
            er.ValueIsMustBeUserProfileTypeError,
            er.DictMustContainsStudentModuleInstanceError
        ) as e:
            self.stderr.write(str(e))
