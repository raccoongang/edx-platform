"""
Signal handlers for offline mode.
"""
from django.dispatch.dispatcher import receiver
from opaque_keys.edx.locator import LibraryLocator

from xmodule.modulestore.django import SignalHandler

from .tasks import generate_offline_content_for_course
from .toggles import is_offline_mode_enabled


@receiver(SignalHandler.course_published)
def update_offline_content_on_course_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Catches the signal that a course has been published in the module
    store and generates offline content for the course.

    Ignores publish signals from content libraries.
    """
    if isinstance(course_key, LibraryLocator):
        return

    if is_offline_mode_enabled(course_key):
        generate_offline_content_for_course.apply_async(kwargs=dict(course_id=str(course_key)))
