"""
This module contains the data models for the import_from_modulestore app.
"""
from collections import namedtuple
from enum import Enum

from django.utils.translation import gettext_lazy as _


class ChoiceMixin(Enum):
    """
    Mixin to provide a method for getting the (value, name) tuple of the enum.
    """

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the value and name of each enum member.
        """
        return [(member.value, member.name) for member in cls if isinstance(member.value, str)]


class ImportStatus(Enum):
    """
    The status of this modulestore-to-learning-core import.
    """

    STAGING = _('Staging content for import')
    STAGING_FAILED = _('Failed to stage content')
    STAGED = _('Content is staged and ready for import')
    IMPORTING = _('Importing staged content')
    IMPORTING_FAILED = _('Failed to import staged content')


class CompositionLevel(ChoiceMixin):
    """
    Enumeration of composition levels for course content.
    Defines the different levels of composition for course content,
    including chapters, sequentials, verticals, and xblocks.
    It also categorizes these levels into complicated and flat
    levels for easier processing.
    """

    CHAPTER = 'chapter'
    SEQUENTIAL = 'sequential'
    VERTICAL = 'vertical'
    XBLOCK = 'xblock'
    COMPLICATED_LEVELS = [CHAPTER, SEQUENTIAL, VERTICAL]
    FLAT_LEVELS = [XBLOCK]

    @classmethod
    def values(cls):
        """
        Returns all simple string values of the CompositionLevel enum.
        """
        return [composition_level.value for composition_level in cls if isinstance(composition_level.value, str)]


PublishableVersionWithMapping = namedtuple('PublishableVersionWithMapping', ['publishable_version', 'mapping'])
