import six
from django.dispatch import receiver

from xmodule.modulestore.django import SignalHandler

from .tasks import generate_course_media


@receiver(SignalHandler.course_published)
def hello_world(sender, course_key, **kwargs):
    import pdb; pdb.set_trace()
    generate_course_media.delay(six.text_type(course_key))
