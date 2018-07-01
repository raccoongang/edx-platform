"""
A convience API for handle common interactions with the Program model.

This is simply a set of functions that can be used elsewhere to abstract some
of the complexities in certain aspects of the codebase, but also to remove the
need to import the Program model elsewhere.

    `get_program_by_program_code` will retreive a specific program object
        based on the `program_code`
    
    `enroll_student_in_program` will enroll the provided `student` into the
        provided `program` (both the `program` and `student` are instances).
        Returns a True or False status to notify if the enrollment was
        successful
    
    `get_enrolled_students` returns the number of students enrolled in a given
        program
    
    `is_enrolled_in_program` will check to see if a student is enrolled in a
        given program
    
    `number_of_enrolled_students` will return the number of students enrolled
        in a given program
    
    `number_of_students_logged_into_access_program` will provide the total
        number of students in a program that have logged into the LMS
    
    `get_courses_locators_for_program` will return a list of the course
        locators containing the locator for module contained within that
        program

    `get_all_programs` will return a Queryset containing every program object
        stored in the `ci_program` model
    
    `student_has_logged_in` will check to see if a specific student has logged
        in
"""
from ci_program.models import Program


def get_program_by_program_code(code):
    """
    Query the database for a specific program based on the program code

    `code` is the code that we use to identify the program

    Returns an instance of the program. Raises a 404 if the program
        doesn't exist
    """
    try:
        return Program.objects.get(program_code=code)
    except Program.DoesNotExist:
        raise Http404("Program with code of %s was not found." % code)


def enroll_student_in_program(program, student):
    """
    Enroll a student in a program.

    `program` is the instance of the program that we want to enroll the
        student in
    `student` is the instance of the user that we wish to enroll

    Returns the status of the enrollment
    """
    enrollment_status = program.enroll_student_in_program(student)
    return enrollment_status


def get_enrolled_students(program):
    """
    Gets a list of the enrolled students enrolled in a given program

    `program` is an instance of the progam that we want to get the list
        of enrolled users from
    
    Returns a list of `user` objects
    """
    return [user for user in program.enrolled_students.all()]


def is_student_enrolled_in_program(code, student):
    """
    Check to see if a given student is enrolled in a given program

    `code` is the course code used as an identifier for a program
    `student` is an instance of the user that we want to check for

    Returns True or False based on whether or not a student is enrolled
        in the program
    """
    program = get_program_by_program_code(code)
    return student.email in get_enrolled_students(program)


def number_of_enrolled_students(program):
    """
    Gets the number of students that are enrolled in a given program

    `program` is the instance of the program that we're interested in

    Returns the total number of students enrolled
    """
    return len(program.enrolled_students.all())


def number_of_students_logged_into_access_program(program):
    """
    Gets the number of students that have logged into the LMS to get
    access to their course content.

    `program` is a program instance.

    Returns the total number of students that have logged
        per-program
    """
    return len([user for user in program.enrolled_students.all() if user.last_login])


def get_courses_locators_for_program(code):
    """
    Get a list of CourseLocator objects for each module in a program

    `code` is the course code used as an identifier for a program

    Returns a list of CourseLocator objects
    """
    program = get_program_by_program_code(code)
    return program.get_course_locators()


def get_all_programs():
    """
    Get a list of all of program codes from the `Program` model
    """
    return Program.objects.all()


def student_has_logged_in(code, student):
    """
    Check to see if a student has logged in to get access to their
    program.

    `code` is the course code used as an identifier for a program
    `student` is the user instance that wish we check for

    Returns a boolean. `False` if `last_login` in `None` and `True` if the
        `last_login` contains a timestamp
    """
    program = get_program_by_program_code(code)
