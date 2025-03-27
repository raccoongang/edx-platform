"""
Factories for CourseToLibraryImport model.
"""

import uuid

import factory
from factory.django import DjangoModelFactory

from common.djangoapps.student.tests.factories import UserFactory

from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport
from openedx.core.djangoapps.content_libraries.tests.factories import ContentLibraryFactory


class CourseToLibraryImportFactory(DjangoModelFactory):
    """
    Factory for CourseToLibraryImport model.
    """

    class Meta:
        model = CourseToLibraryImport

    course_ids = ' '.join([f'course-v1:edX+DemoX+Demo_Course{i}' for i in range(1, 3)])
    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    content_library = factory.SubFactory(ContentLibraryFactory)
    user = factory.SubFactory(UserFactory)
