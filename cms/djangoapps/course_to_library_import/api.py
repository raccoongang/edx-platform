"""
API for course to library import.
"""

from .constants import COURSE_TO_LIBRARY_IMPORT_PURPOSE
from .models import CourseToLibraryImport
from .tasks import (
    import_course_staged_content_to_library_task,
    save_courses_to_staged_content_task,
)
from .types import CompositionLevel


def import_course_staged_content_to_library(
    library_key: str,
    user_id: int,
    usage_ids: list[str],
    import_id: str,
    composition_level: CompositionLevel,
    override: bool
) -> None:
    """
    Import staged content to a library.
    """
    import_course_staged_content_to_library_task.delay(
        user_id,
        usage_ids,
        library_key,
        COURSE_TO_LIBRARY_IMPORT_PURPOSE,
        import_id,
        composition_level,
        override,
    )


def create_import(
    course_ids: list[str], user_id: int, library_key: str
) -> CourseToLibraryImport:
    """
    Create a new import task to import a course to a library.
    """
    course_to_library_import = CourseToLibraryImport(
        course_ids=" ".join(course_ids),
        library_key=library_key,
        user_id=user_id,
    )
    course_to_library_import.save()

    save_courses_to_staged_content_task.delay(
        course_ids,
        user_id,
        course_to_library_import.id,
        COURSE_TO_LIBRARY_IMPORT_PURPOSE,
    )
    return course_to_library_import
