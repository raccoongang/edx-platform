import six
from django.dispatch import receiver
from openedx_events.content_authoring.signals import XBLOCK_PUBLISHED


from xmodule.modulestore.django import SignalHandler

from .tasks import generate_course_media
from .utils.assets_management import remove_old_files


@receiver([XBLOCK_PUBLISHED])
def listen_xblock_publish(**kwargs):
    if MEDIA_GENERATION_ENABLED.is_disabled():
        return
    usage_key = UsageKey.from_string(kwargs.get('usage_key_string'))
    xblock = modulestore().get_item(usage_key)
    remove_old_files(xblock)

