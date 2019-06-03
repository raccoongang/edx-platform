from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import Signal, receiver
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from .tasks import task_reindex_course, task_reindex_courses


class CourseCategory(MPTTModel):
    name = models.CharField(max_length=255, verbose_name=_("Category Name"), unique=True)
    description = models.TextField(null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    enabled = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def get_course_ids(self, **kwargs):
        qs = self.coursecategorycourse_set.filter(**kwargs)
        return [c.course_id for c in qs]

    def __unicode__(self):
        return self.name

    @classmethod
    def get_category_tree(cls, **kwargs):
        def add_nodes(nodes):
            tree = {}
            for node in nodes:
                tree[node] = None
                if not node.is_leaf_node():
                    tree[node] = add_nodes(node.children.filter(**kwargs))
            return tree

        return add_nodes(cls.objects.filter(parent=None, **kwargs))


class CourseCategoryCourse(models.Model):
    course_category = models.ForeignKey(CourseCategory, null=True)
    course_id = CourseKeyField(max_length=255, db_index=True, verbose_name=_("Course"))

    class Meta(object):
        unique_together = ('course_category', 'course_id')


@receiver(post_save, sender=CourseCategory)
def reindex_course_category(sender, instance, **kwargs):
    task_reindex_courses.delay(instance.id)


@receiver(post_delete, sender=CourseCategoryCourse)
def reindex_course(sender, instance, **kwargs):
    task_reindex_course.delay(unicode(instance.course_id))
