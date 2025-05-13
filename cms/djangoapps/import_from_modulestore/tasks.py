"""
Tasks for course to library import.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from edx_django_utils.monitoring import set_code_owner_attribute_from_module

from openedx_learning.api import authoring as authoring_api
from openedx_learning.api.authoring_models import LearningPackage
from openedx.core.djangoapps.content_staging import api as content_staging_api
from user_tasks.models import UserTaskStatus
from user_tasks.tasks import UserTask

from .constants import IMPORT_FROM_MODULESTORE_PURPOSE
from .data import ImportStatus
from .helpers import get_items_to_import, ImportClient
from .models import Import, PublishableEntityImport, StagedContentForImport
from .validators import validate_composition_level

log = get_task_logger(__name__)


class ImportCourseTask(UserTask):
    """
    Base class for import course tasks.
    """

    @staticmethod
    def calculate_total_steps(arguments_dict):
        """
        Get number of in-progress steps in importing process, as shown in the UI.

        For reference, these are:

        1. Staging course content
        2. Importing staged content into library
        """
        return 2

    @classmethod
    def generate_name(cls, arguments_dict):
        """
        Create a name for this particular import task instance.

        Arguments:
            arguments_dict (dict): The arguments given to the task function

        Returns:
            str: The generated name
        """
        library_id = arguments_dict.get('learning_package_id')
        import_id = arguments_dict.get('import_pk')
        return f'Import course to library (library_id={library_id}, import_id={import_id})'


@shared_task(base=ImportCourseTask, bind=True)
# Note: The decorator @set_code_owner_attribute cannot be used here because the UserTaskMixin
#   does stack inspection and can't handle additional decorators.
def import_course_to_library_task(
    self,
    import_pk: int,
    usage_keys_string: list[str],
    learning_package_id: int,
    user_id: int,
    composition_level: str,
    override: bool,
) -> None:
    """
    Import course to library task.

    1. Save course to staged content task by sections/chapters.
    2. Import staged content to library task.
    """
    set_code_owner_attribute_from_module(__name__)

    # Step 1: Save course to staged content task by sections/chapters.
    try:
        import_event = Import.objects.get(pk=import_pk, user_id=user_id)
        import_event.status = self.status
        import_event.save(update_fields=['status'])
    except Import.DoesNotExist:
        log.info('Import event not found for pk %s', import_pk)
        return

    import_event.clean_related_staged_content()
    import_event.set_status(ImportStatus.STAGING)
    try:
        with transaction.atomic():
            items_to_import = get_items_to_import(import_event)
            for item in items_to_import:
                staged_content = content_staging_api.stage_xblock_temporarily(
                    item,
                    import_event.user.id,
                    purpose=IMPORT_FROM_MODULESTORE_PURPOSE,
                )
                StagedContentForImport.objects.create(
                    staged_content=staged_content,
                    import_event=import_event,
                    source_usage_key=item.location
                )

            if items_to_import:
                import_event.set_status(ImportStatus.STAGED)
            else:
                import_event.set_status(ImportStatus.STAGING_FAILED)
    except Exception as exc:
        import_event.set_status(ImportStatus.STAGING_FAILED)
        raise exc

    # Step 2: Import staged content to library task.
    self.status.increment_completed_steps()

    validate_composition_level(composition_level)
    try:
        target_learning_package = LearningPackage.objects.get(id=learning_package_id)
    except LearningPackage.DoesNotExist:
        log.info('Target learning package not found')
        return

    import_event.set_status(ImportStatus.IMPORTING)
    imported_publishable_versions = []
    with authoring_api.bulk_draft_changes_for(learning_package_id=learning_package_id) as change_log:
        try:
            for usage_key_string in usage_keys_string:
                if staged_content_item := import_event.get_staged_content_by_source_usage_key(usage_key_string):
                    import_client = ImportClient(
                        import_event,
                        usage_key_string,
                        target_learning_package,
                        staged_content_item,
                        composition_level,
                        override,
                    )
                    imported_publishable_versions.extend(import_client.import_from_staged_content())
        except Exception as exc:
            import_event.set_status(ImportStatus.IMPORTING_FAILED)
            raise exc

    import_event.set_status(UserTaskStatus.SUCCEEDED)
    for imported_component_version in imported_publishable_versions:
        PublishableEntityImport.objects.create(
            import_event=import_event,
            resulting_mapping=imported_component_version.mapping,
            resulting_change=change_log.records.get(entity=imported_component_version.mapping.target_entity),
        )
