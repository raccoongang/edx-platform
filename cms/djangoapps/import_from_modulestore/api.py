"""
API for course to library import.
"""

from .models import Import as _Import
from .tasks import import_course_to_library_task
from .validators import validate_composition_level, validate_usage_keys_to_import


def import_course_to_library(
    source_key: str,
    target_change_id: int,
    user_id: int,
    usage_ids: list[str],
    learning_package_id: int,
    composition_level: str,
    override: bool,
) -> None:
    """
    Create a new import event to import a course to a library, save course to staged content
    and import staged content to library.
    """
    validate_composition_level(composition_level)
    validate_usage_keys_to_import(usage_ids)

    import_from_modulestore = _Import.objects.create(
        source_key=source_key,
        target_change_id=target_change_id,
        user_id=user_id,
    )

    kwargs = {
        'import_pk': str(import_from_modulestore.pk),
        'usage_keys_string': usage_ids,
        'learning_package_id': learning_package_id,
        'user_id': user_id,
        'composition_level': composition_level,
        'override': override,
    }
    import_course_to_library_task.delay(**kwargs)
    return import_from_modulestore
