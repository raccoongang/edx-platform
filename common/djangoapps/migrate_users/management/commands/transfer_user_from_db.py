"""
Manage.py command for migrate users with progress.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from migrate_users import utils
from migrate_users import error as er
from migrate_users.remote_db_helpers import RemoteDBQuery


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
            count_of_processed_users = {}
            # Contain error for crete users: key: remote user id value: error string
            dict_with_error_processing = {}

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
                        # If is_created = True, the save_user_information method created a new user object.
                        # If is_created = False, the save_user_information method found and
                        # returned a existing user object.
                        user, is_created = utils.save_user_information(user_info)
                        # Work with UserSocialAuth
                        user_social_auth = remote_db_query.get_user_social_auth_by_id(user_id)
                        if user_social_auth:
                            self.stdout.write("Create UserSocialAuth")
                            utils.save_user_social_auth(user_social_auth[0], user)

                        # If is_created = True, we need to create a UserPreference and a LanguageProficiency.
                        # If is_created = False, we use a existing user object with these preferences.
                        if is_created:
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

                        if is_created:
                            self.stdout.write("User created ({id}): {user}, profile: {profile}".format(
                                id=user.id,
                                user=user,
                                profile=user.profile
                            ))
                        else:
                            self.stdout.write(
                                "Existing User({id}) received the progress: {user}, profile: {profile}".format(
                                    id=user.id,
                                    user=user,
                                    profile=user.profile
                                )
                            )
                        count_of_processed_users[str(user_id)] = str(user.id)
                except (
                    er.UserInformationDoesNotExistsInRemoteDBError,
                    er.UserAlreadyExistsError,
                    er.ValidationUserError,
                    er.ValidationUserSocialAuthError,
                    er.ValidationUserPreferenceError,
                    er.ValidationLanguageProficiencyError,
                ) as e:
                    self.stderr.write(str(e))
                    dict_with_error_processing[str(user_id)] = str(e)

            # Test of rebase users and write total information

            self.stdout.write("Total Information:")
            self.stdout.write("__________________")
            # Information about created uses and errors
            self.stdout.write(
                "Processed {count_of_users} users out of {count_remote_user_for_rebase} users".format(
                    count_of_users=len(count_of_processed_users),
                    count_remote_user_for_rebase=len(user_id_list)
                )
            )
            if count_of_processed_users:
                # information about errors
                if dict_with_error_processing:
                    self.stderr.write("Count of errors: {errors}: ".format(errors=len(dict_with_error_processing)))
                    self.stderr.write("_______________")
                    for key, value in dict_with_error_processing.items():
                        self.stderr.write(
                            "Error for User with remote id {remote_id}: {error}".format(
                                remote_id=key,
                                error=value
                            )
                        )

        except er.WrongConnectionNameError as e:
            self.stderr.write(str(e))
        except (
            er.ValueIsMustBeDictionaryError,
            er.ValueIsMustBeListOrTupleError,
            er.ValueIsMustBeUserTypeError,
            er.ValueIsMustBeUserProfileTypeError,
        ) as e:
            self.stderr.write(str(e))
