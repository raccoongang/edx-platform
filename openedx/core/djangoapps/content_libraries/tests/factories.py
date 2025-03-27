"""
Factories for content_libraries models.
"""
import factory
from factory.django import DjangoModelFactory
from organizations.tests.factories import OrganizationFactory

from openedx.core.djangoapps.content_libraries.api import ContentLibrary


class ContentLibraryFactory(DjangoModelFactory):
    """
    Factory for ContentLibrary model.
    """

    class Meta:
        model = ContentLibrary

    org = factory.SubFactory(OrganizationFactory)
    license = factory.Faker('sentence')
    slug = factory.Faker('slug')

