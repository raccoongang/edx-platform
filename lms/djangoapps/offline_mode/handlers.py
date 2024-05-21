import six
from django.dispatch import receiver
from openedx_events.content_authoring.signals import XBLOCK_PUBLISHED

from xmodule.modulestore.django import SignalHandler

from .tasks import generate_course_media


@receiver([XBLOCK_PUBLISHED])
def listen_course_publish(**kwargs):
    if USER_TOURS_DISABLED.is_disabled():
        return
    generate_course_media.delay(six.text_type(course_key))
