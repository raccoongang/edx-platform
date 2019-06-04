import django.dispatch
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import Signal, receiver
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from .tasks import task_reindex_courses

move_to = django.dispatch.Signal()


class CourseCategory(MPTTModel):
    name = models.CharField(max_length=255, verbose_name=_("Category Name"), unique=True)
    description = models.TextField(null=True, blank=True)
    img = models.ImageField(upload_to='course_category', blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    enabled = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    courses = models.ManyToManyField("course_overviews.CourseOverview", blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def get_course_ids(self, **kwargs):
        qs = self.coursecategorycourse_set.filter(**kwargs)
        return [c.course_id for c in qs]

    def __unicode__(self):
        return self.name

    def move_to(self, target, position='first-child'):
        self._tree_manager.move_node(self, target, position)
        move_to.send(sender=self.__class__, instance=self)

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

    class Meta:
        unique_together = ('course_category', 'course_id')


@receiver(move_to, sender=CourseCategory)
def move_reindex_course_category(sender, instance, **kwargs):
    task_reindex_courses.delay(category_id=instance.id)


@receiver(m2m_changed, sender=CourseCategory.courses.through)
def save_reindex_course_category(sender, instance, pk_set, action, **kwargs):
    if action == 'pre_clear':
        instance.pre_clear_course_keys = set()
        for courses in instance.courses.all():
            instance.pre_clear_course_keys.add(str(courses.id))
    if action == 'post_add':
        courses_set = set()
        for courses in instance.courses.all():
            courses_set.add(str(courses.id))
        courses_set.update(instance.pre_clear_course_keys)
        task_reindex_courses.delay(instance.id, list(courses_set))
