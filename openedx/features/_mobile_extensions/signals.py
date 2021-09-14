import six
from django.dispatch import receiver

from xmodule.modulestore.django import SignalHandler

from .tasks import update_html_block_mobile_api


@receiver(SignalHandler.course_published)
def listen_for_course_publish(sender, course_key, **kwargs):
    update_html_block_mobile_api.delay(six.text_type(course_key))
