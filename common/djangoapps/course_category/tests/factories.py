"""Provides factories for course_category utils."""
import factory
from course_category.models import CourseCategory
from factory.django import DjangoModelFactory


class CourseCategoryFactory(DjangoModelFactory):

    class Meta(object):
        model = CourseCategory
        django_get_or_create = ('name',)

    name = factory.Sequence(u'category{0}'.format)
    description = 'test category description'
    enabled = True
    slug = name

    @factory.post_generation
    def courses(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for course in extracted:
                self.courses.add(course)
