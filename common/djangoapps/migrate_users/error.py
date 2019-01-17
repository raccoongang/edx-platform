"""
Errors in model.
"""


class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    class_message = "Error"
    
    def __init__(self, *args):
        self.value = " ".join(args)

    def __str__(self):
        return repr("{}: {}".format(self.class_message, self.value))


class WrongConnectionNameError(Error):
    class_message = "Wrong connection name"


class UserAlreadyExistsError(Error):
    class_message = "User already exists"

    
class UserInformationDoesNotExistsInRemoteDBError(Error):
    class_message = "User's information does not exists in remote DB"


class CreateUserError(Error):
    class_message = "Create User Error"


class ValidationUserError(Error):
    class_message = "Some user's information are incorrect"

    
class ValidationUserSocialAuthError(Error):
    class_message = "UserSocialAuth information is incorrect"

    
class ValidationUserPreferenceError(Error):
    class_message = "UserPreference is incorrect"

    
class ValidationLanguageProficiencyError(Error):
    class_message = "LanguageProficiency code is incorrect"

    
class ValidationCourseEnrollmentError(Error):
    class_message = "CourseEnrollment information is incorrect"

    
class ValidationStudentModuleError(Error):
    class_message = "StudentModule information is incorrect"

    
class ValidationStudentModuleHistoryError(Error):
    class_message = "StudentModuleHistory information is incorrect"

    
class DictMustContainsStudentModuleInstanceError(Error):
    class_message = "Dictionary must contains StudentModule instance"

   
class ValueIsMustBeUserTypeError(Error):
    class_message = "Value must be a User type"


class ValueIsMustBeUserProfileTypeError(Error):
    class_message = "Value must be a UserProfile type"

    
class ValueIsMustBeListOrTupleError(Error):
    class_message = "Value must be a list or a tuple"

    
class ValueIsMustBeDictionaryError(Error):
    class_message = "Value must be a dict"
