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
        query = "SELECT id FROM nrg_edxapp.auth_user;"
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
            FROM  nrg_edxapp.auth_user Join nrg_edxapp.auth_userprofile
            ON nrg_edxapp.auth_userprofile.user_id = nrg_edxapp.auth_user.id
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
            FROM nrg_edxapp.social_auth_usersocialauth Where user_id = {user_id};
        """.format(user_id=user_id)
        return self.remote_db.execute(query)
    
    def get_user_preferences_by_user_id(self, user_id):
        """
        Get User's preference.
        
        :param user_id: User id in remote DB.
        :return: List of dictionary with user's Preference.
        """
        query = """
            SELECT `key`, value FROM nrg_edxapp.user_api_userpreference WHERE user_id = {user_id};
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
            FROM nrg_edxapp.student_languageproficiency
            WHERE user_profile_id = {user_profile_id};
        """.format(user_profile_id= user_profile_id)
        return self.remote_db.execute(query)
    
    def get_course_enrollments(self, user_id, courses_id_list=None):
        """
        Get course enrollment for user in remote DB.
        
        :param user_id: User id in remote DB.
        :param courses_id_list: List of Course key or None.
        :return: List of Dictionaries with course enrollments for current user.
        """
        if courses_id_list and not isinstance(courses_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(courses_id_list)
                )
            )
        courses_query = ""
        if courses_id_list:
            courses_query = "AND course_id IN ('{courses_id}')".format(courses_id="', '".join(courses_id_list))
        query = """
            SELECT id, course_id, created, is_active, mode, user_id
            FROM nrg_edxapp.student_courseenrollment
            WHERE user_id = {user_id} {courses_query};
        """.format(user_id=user_id, courses_query=courses_query)
        return self.remote_db.execute(query)
    
    def get_student_modules(self, user_id, courses_id_list=None):
        """
        Get student modules in course by user id in remote DB.
        
        :param user_id: User id in remote DB.
        :param courses_id_list: List of Course key or None.
        :return: List of Dictionaries with student modules data.
        """
        if courses_id_list and not isinstance(courses_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(courses_id_list)
                )
            )
        courses_query = ""
        if courses_id_list:
            courses_query = "AND course_id IN ('{courses_id}')".format(courses_id="', '".join(courses_id_list))
        query = """
            SELECT id, module_type, module_id, course_id, state, grade,
            max_grade, done, created, modified, student_id
            FROM nrg_edxapp.courseware_studentmodule
            WHERE student_id={user_id} {courses_query};
        """.format(user_id=user_id, courses_query=courses_query)
        return self.remote_db.execute(query)
    
    def get_student_module_history(self, student_module_id_list):
        """
        Get student module history by student modules id in remote DB.
        
        :param student_module_id_list: student modules id in remote DB.
        :return: List of Dictionaries with student module history.
        """
        if student_module_id_list and not isinstance(student_module_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(student_module_id_list)
                )
            )
        query = """
            SELECT id, version, created, state, grade, max_grade, student_module_id
            FROM nrg_edxapp.courseware_studentmodulehistory
            WHERE student_module_id IN ('{studentmodule}');
        """.format(studentmodule="', '".join(student_module_id_list))
        return self.remote_db.execute(query)

    def get_course_enrollments_count(self, user_id_list, courses_id_list=None):
        """
        Get course enrollment for user in remote DB.

        :param user_id_list: User id in remote DB.
        :param courses_id_list: List of Course key or None.
        :return: List of Dictionaries with course enrollments for current user.
        """
        if not isinstance(user_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(user_id_list)
                )
            )
        if courses_id_list and not isinstance(courses_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(courses_id_list)
                )
            )
        courses_query = ""
        if courses_id_list:
            courses_query = "AND course_id IN ('{courses_id}')".format(courses_id="', '".join(courses_id_list))
        query = """
               SELECT COUNT(id) as count FROM nrg_edxapp.student_courseenrollment
               WHERE user_id IN ('{user_id}') {courses_query};
           """.format(user_id="', '".join(user_id_list), courses_query=courses_query)
        return self.remote_db.execute(query)

    def get_student_modules_count(self, user_id_list, courses_id_list=None):
        """
        Get student modules in course by user id in remote DB.

        :param user_id_list: User id in remote DB.
        :param courses_id_list: List of Course key or None.
        :return: List of Dictionaries with student modules data.
        """
        if not isinstance(user_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(user_id_list)
                )
            )
        if courses_id_list and not isinstance(courses_id_list, (list, tuple)):
            raise ValueIsMustBeListOrTupleError(
                "Variable type is {variable_type}".format(
                    variable_type=type(courses_id_list)
                )
            )
        courses_query = ""
        if courses_id_list:
            courses_query = "AND course_id IN ('{courses_id}')".format(courses_id="', '".join(courses_id_list))
        query = """
               SELECT COUNT(id) as count FROM nrg_edxapp.courseware_studentmodule
               WHERE student_id IN ('{user_id}') {courses_query};
           """.format(user_id="', '".join(user_id_list), courses_query=courses_query)
        return self.remote_db.execute(query)
