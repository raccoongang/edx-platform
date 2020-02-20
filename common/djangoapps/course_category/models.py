import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext as _

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore

log = logging.getLogger(__name__)


class CourseCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), unique=True)
    courses = models.ManyToManyField(
        CourseOverview,
        related_name='course_categories',
        blank=True,
        verbose_name=_('Courses')
    )

    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")

    def delete(self, *args, **kwargs):
        """
        Override model's delete method to maintain consistency with mongo
        """
        self.process_course_category_deletion()
        super(CourseCategory, self).delete(*args, **kwargs)

    @classmethod
    def update_course_category_models(cls, course_key, course_category_list):
        if course_category_list is None:
            course_category_ids_list = []
        else:
            course_category_ids_list = [x.strip('course_category_') for x in course_category_list]
        course_overview = CourseOverview.get_from_id(course_key)
        course_categories = cls.objects.filter(id__in=course_category_ids_list)
        course_overview.course_categories = course_categories

    def process_course_category_deletion(self):
        store = modulestore()
        superuser = get_user_model().objects.filter(is_superuser=True, is_active=True).first()
        if superuser is None:
            log.exception("Failed to delete category. At least one superuser should be configured.")
            return

        category_id_field = 'course_category_{}'.format(self.id)
        for course_key in self.courses.values_list('id', flat=True):
            course_descriptor = store.get_course(course_key)
            course_categories_list = course_descriptor.course_category
            if category_id_field in course_categories_list:
                course_categories_list.remove(category_id_field)
            course_descriptor.course_category = course_categories_list
            store.update_item(course_descriptor, superuser.id)
