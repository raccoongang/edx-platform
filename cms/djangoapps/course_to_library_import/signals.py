"""
Signals for CourseToLibraryImport.
"""


from django.dispatch import receiver
from django.db.models.signals import post_save

from .constants import COURSE_TO_LIBRARY_IMPORT_PURPOSE
from .models import CourseToLibraryImport
from .tasks import save_courses_to_staged_content_task


@receiver(post_save, sender=CourseToLibraryImport)
def save_courses_to_staged_content(sender, instance, created, **kwargs):
    """
    Save courses to staged content when a CourseToLibraryImport is created.
    """
    if created:
        save_courses_to_staged_content_task.delay(
            course_ids=instance.course_ids.split(),
            user_id=instance.user_id,
            import_task_id=instance.id,
            purpose=COURSE_TO_LIBRARY_IMPORT_PURPOSE,
        )
