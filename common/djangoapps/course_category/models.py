from django.db import models
from django.db.models.signals import m2m_changed, pre_delete, post_delete, post_save, post_init
from django.dispatch import Signal, receiver
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField

from mptt.models import MPTTModel, TreeForeignKey
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from .tasks import task_reindex_courses

move_to = Signal()


class Program(models.Model):
    title = models.CharField(max_length=100)
    uuid = models.CharField(primary_key=True, max_length=50)
    subtitle = models.TextField(default='')
    courses = JSONField(default=[])
    products = models.ManyToManyField("course_overviews.CourseOverview")

    def __unicode__(self):
        """Represent ourselves with the course key."""
        return unicode(self.title)


class CourseCategory(MPTTModel):
    name = models.CharField(max_length=255, verbose_name=_("Category Name"), unique=True)
    description = models.TextField(null=True, blank=True)
    img = models.ImageField(upload_to='course_category', blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    enabled = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    courses = models.ManyToManyField("course_overviews.CourseOverview")
    programs = models.ManyToManyField(Program, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Course Categories'

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


@receiver(move_to, sender=CourseCategory)
def move_reindex_course_category(sender, instance, **kwargs):
    task_reindex_courses.delay(instance.id)


@receiver([pre_delete, post_delete], sender=CourseCategory)
def delete_reindex_course_category(sender, instance, **kwargs):
    category_courses = instance.courses.all()
    if category_courses:
        instance.courses_list = [str(c.id) for c in category_courses]
    elif getattr(instance, 'courses_list', []):
        task_reindex_courses.delay(course_keys=instance.courses_list)


@receiver(m2m_changed, sender=CourseCategory.courses.through)
def save_reindex_course_category(sender, instance, pk_set, action, **kwargs):
    courses_set = set()
    if action == 'pre_remove':
        instance.pre_clear_course_keys = set()
        instance.pre_clear_course_keys.update(str(x.id) for x in instance.courses.all())

    if action in ['post_add', 'post_remove']:
        courses_set.update(str(c.id) for c in instance.courses.all())
        courses_set.update(getattr(instance, 'pre_clear_course_keys', set()))
        task_reindex_courses.delay(instance.id, list(courses_set))


@receiver(post_init, sender=CourseCategory)
def remember_previous_name(sender, instance, **kwargs):
    """
    Saves category name to check if it was changed.
    """
    instance.previous_name = instance.name


@receiver(post_save, sender=CourseCategory)
def category_name_change_reindex_course_category(sender, instance, created, **kwargs):
    """
    Reindexes category courses when category name changes.

    We need to reindex category courses (in case of category name was changed
    but not category courses) to avoid category disappearing in category
    filters (catalog and index page).
    """
    courses=[str(c.id) for c in instance.courses.all()]
    if (instance.previous_name != instance.name and not created):
        task_reindex_courses.delay(instance.id, courses)
