""""
Python API for course to library import
=======================================
"""

from .models import CourseToLibraryImport


def create_import(course_key, library_key, source_type):
    """
    Create a new import task to import a course to a library.

    Args:
        course_key (str): The course key of the course to import.
        library_key (str): The key of the library to import the course to.
        source_type (str): The type of the source of the import.
    """
    import_task = CourseToLibraryImport(
        course_id=course_key,
        library_key=library_key,
        source_type=source_type
    )
    import_task.save()

    return import_task


def get_import(import_id):
    """
    Get an import task by its ID.

    Args:
        import_id (int): The ID of the import task to get.

    Returns:
        CourseToLibraryImport: The import task.
    """
    return CourseToLibraryImport.objects.get(id=import_id)


def get_imports():
    """
    Get all import tasks.

    Returns:
        QuerySet: The import tasks.
    """
    return CourseToLibraryImport.objects.all()
