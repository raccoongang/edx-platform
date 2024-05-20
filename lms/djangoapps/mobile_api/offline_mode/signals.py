import six
from django.dispatch import receiver
from openedx_events.content_authoring.signals import (
    XBLOCK_CREATED,
    XBLOCK_DELETED,
    XBLOCK_DUPLICATED,
    XBLOCK_UPDATED,
    XBLOCK_PUBLISHED,
)

from xmodule.modulestore.django import SignalHandler

from .tasks import generate_course_media


@receiver([XBLOCK_PUBLISHED])
def hello_world(**kwargs):
    import pdb; pdb.set_trace()
    pass
    # generate_course_media.delay(six.text_type(course_key))
