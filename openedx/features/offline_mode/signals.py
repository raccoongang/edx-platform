"""
Signal handlers for offline mode.
"""
from django.dispatch.dispatcher import receiver
from opaque_keys.edx.locator import LibraryLocator

from xmodule.modulestore.django import SignalHandler

from .tasks import generate_offline_content_for_course
from .assets_management import get_offline_course_total_size
from .models import OfflineCourseSize


@receiver(SignalHandler.course_cache_updated)
def generate_offline_content_on_course_cache_update(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Catches the signal that a course has been updated in the module
    store and generates offline content for the course.
    Ignores cache update signals from content libraries.
    """
    if isinstance(course_key, LibraryLocator):
        return

    generate_offline_content_for_course.apply_async([str(course_key)])


@receiver(SignalHandler.item_deleted)
def handle_item_deleted(**kwargs):
    """
    Handles the deletion of an item from the module store and updates the course offline size.
    """
    usage_key = kwargs.get('usage_key')
    if usage_key:
        course_key = usage_key.course_key

        total_offline_course_size = get_offline_course_total_size(course_key)
        OfflineCourseSize.objects.update_or_create(course_id=course_key, defaults={'size': total_offline_course_size})
