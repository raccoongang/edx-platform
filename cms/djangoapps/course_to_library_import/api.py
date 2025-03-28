"""
API for course to library import.
"""
from opaque_keys.edx.locator import LibraryLocatorV2

from openedx.core.djangoapps.content_libraries.api import ContentLibrary
from .models import CourseToLibraryImport as _CourseToLibraryImport
from .tasks import import_course_staged_content_to_library_task,  save_courses_to_staged_content_task
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
        import_id,
        composition_level,
        override,
    )


def create_import(course_ids: list[str], user_id: int, library_id: str) -> _CourseToLibraryImport:
    """
    Create a new import task to import a course to a library.
    """
    content_library = ContentLibrary.objects.get_by_key(LibraryLocatorV2.from_string(library_id))
    course_to_library_import = _CourseToLibraryImport(
        course_ids=" ".join(course_ids),
        content_library=content_library,
        user_id=user_id,
    )
    course_to_library_import.save()
    save_courses_to_staged_content_task.delay(user_id, course_to_library_import.uuid)
    return course_to_library_import
