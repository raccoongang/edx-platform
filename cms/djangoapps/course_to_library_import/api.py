""""
API for course to library import.
"""

from .tasks import save_course_to_staged_content_task

COURSE_TO_LIBRARY_IMPORT_PURPOSE = "course_to_library_import"


def save_course_to_staged_content(
    course_id: str,
    user_id: int,
    purpose: str = COURSE_TO_LIBRARY_IMPORT_PURPOSE,
    version_num: int | None = None,
) -> None:
    """
    Save course to staged content.
    """
    save_course_to_staged_content_task.delay(course_id, user_id, purpose, version_num)
