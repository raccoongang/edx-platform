import hashlib

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class WebScienceCourseOverview(models.Model):
    course = models.OneToOneField(
        CourseOverview,
        related_name='web_science',
        on_delete=models.CASCADE,
    )
    color = models.CharField(max_length=7)
    image = models.CharField(max_length=254)

    @staticmethod
    def get_from_key(course_key):
        course = CourseOverview.objects.get(id=course_key)
        return WebScienceCourseOverview.objects.get_or_create(course=course)[0]

    def apply_to(self, obj):
        obj.web_science_color = self.color
        obj.web_science_image = self.image
        return obj

    def update_from_json(self, data):
        self.color = data['web_science_color']
        self.image = data['web_science_image']
        self.save()

    @property
    def course_hash(self):
        return hashlib.sha1(unicode(self.course.id)).hexdigest()

    def __unicode__(self):
        return u'{} - {} - {}'.format(self.course, self.color, self.image)

    class Meta(object):
        verbose_name = u'Course settings'
        verbose_name_plural = u'Course settings'


@receiver([post_save, post_delete], sender=WebScienceCourseOverview)
def clear_css_cache(**kwargs):
    key = make_template_fragment_key('web_science_generate_css')
    cache.delete(key)
