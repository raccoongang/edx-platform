"""
Work with remote DB.
"""
from django.db import connections, transaction

from migrate_users.error import ValueIsMustBeListOrTupleError, WrongConnectionNameError


class RemoteDBORM(object):
    """
    Class for help get information in DB.
    """
    def __init__(self, connection_name):
        if connections.databases.get(connection_name):
            self.connection_name = connection_name
        else:
            raise WrongConnectionNameError(connection_name)
     
    def execute(self, query_string):
        """
        Run SQL query in string and return information.
        
        :param query_string: Sql query in string.
        :return: List of dictionaries or empty list.
        """
        with transaction.atomic():
            with connections[self.connection_name].cursor() as cursor:
                cursor.execute(query_string)
                columns = [col[0] for col in cursor.description]
                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
    
    def __unicode__(self):
        return u"connection_name: {}".format(self.connection_name)


class RemoteDBQuery(object):
    """
    Class for working with remote DB.
    """
    
    def __init__(self, connection_name):
        self.remote_db = RemoteDBORM(connection_name)

    def get_users_id_list_from_course_id(self, courses_id_list):
        """
        Return user id list form list of course id.
        
        :param courses_id_list:  List of course id.
        :return: List of dictionary with users id.
        """
        if not courses_id_list:
            return []
        if not isinstance(courses_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(courses_id_list)
                )
            )
        query = """
            SELECT DISTINCT user_id FROM student_historicalcourseenrollment WHERE
            student_historicalcourseenrollment.course_id IN ('{courses_id}')
        """.format(courses_id="', '".join(courses_id_list))
        return self.remote_db.execute(query)
    
    def get_all_users_id(self):
        """
        Get all users id.
        
        :return: List of dictionary with users id.
        """
        query = "SELECT id FROM auth_user;"
        return self.remote_db.execute(query)

    def get_user_information_by_id(self, user_id):
        """
        Get User information by id.
        
        :param user_id: User id in remote DB.
        :return: List of dictionary with user information.
        """
        query = """
            SELECT auth_user.* , auth_userprofile.id as userprofile_id, auth_userprofile.name,
            auth_userprofile.meta, auth_userprofile.courseware, auth_userprofile.language,
            auth_userprofile.location, auth_userprofile.year_of_birth, auth_userprofile.gender,
            auth_userprofile.level_of_education, auth_userprofile.mailing_address,
            auth_userprofile.city, auth_userprofile.country, auth_userprofile.goals,
            auth_userprofile.allow_certificate, auth_userprofile.bio,
            auth_userprofile.profile_image_uploaded_at,
            auth_userprofile.user_id as userprofile_user_id
            FROM  auth_user Join auth_userprofile
            ON auth_userprofile.user_id = auth_user.id
            WHERE auth_user.id = {user_id}
        """.format(user_id=user_id)
        return self.remote_db.execute(query)

    def get_user_social_auth_by_id(self, user_id):
        """
        Get User social Auth by user id.
        
        :param user_id: User id in remote DB.
        :return: List of dictionary with UserSocialAuth information.
        """
        query = """
            SELECT id, provider, uid, extra_data, user_id
            FROM social_auth_usersocialauth Where user_id = {user_id};
        """.format(user_id=user_id)
        return self.remote_db.execute(query)
    
    def get_user_preferences_by_user_id(self, user_id):
        """
        Get User's preference.
        
        :param user_id: User id in remote DB.
        :return: List of dictionary with user's Preference.
        """
        query = """
            SELECT `key`, value FROM user_api_userpreference WHERE user_id = {user_id};
        """.format(user_id=user_id)
        return self.remote_db.execute(query)
    
    def get_student_language_proficiency_by_profile_id(self, user_profile_id):
        """
        Get student language proficiency in remote DB.
        
        :param user_profile_id: UserProfile id in remote DB.
        :return: List of dictionary with student language proficiency data.
        """
        query = """
            SELECT code, user_profile_id
            FROM student_languageproficiency
            WHERE user_profile_id = {user_profile_id};
        """.format(user_profile_id= user_profile_id)
        return self.remote_db.execute(query)
