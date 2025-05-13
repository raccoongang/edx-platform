"""
Tests for import_from_modulestore helpers.
"""
from unittest import mock
from unittest.mock import patch
import pytest
from datetime import datetime, timezone
from lxml import etree
from django.test import TestCase
from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.locator import LibraryLocator
from openedx.core.djangoapps.content_libraries.api import ContentLibrary
from openedx_learning.api.authoring_models import (
    Component, ContainerVersion, PublishableEntity, LearningPackage
)
from ..helpers import ImportClient
from ..models import Import


# pylint: disable=protected-access
@pytest.mark.django_db
class TestImportClient(TestCase):
    """Tests for ImportClient class."""

    def setUp(self):
        super().setUp()
        self.import_event = mock.MagicMock(spec=Import)
        self.import_event.user_id = "test_user"

        self.block_usage_key = "block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical1"

        self.learning_package = mock.MagicMock(spec=LearningPackage)
        self.content_library = mock.MagicMock(spec=ContentLibrary)
        self.content_library.library_key = LibraryLocator.from_string("library-v1:edX+lib1")
        self.learning_package.contentlibrary = self.content_library

        self.staged_content = mock.MagicMock()
        self.staged_content.id = "test_staged_content"
        self.staged_content.olx = "<vertical url_name='vertical1'><html url_name='html1'>Content</html></vertical>"
        self.staged_content.tags = [
            "block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical1",
            "block-v1:edX+DemoX+Demo_Course+type@html+block@html1",
        ]

        self.composition_level = "vertical"

        self.client = ImportClient(
            self.import_event,
            self.block_usage_key,
            self.learning_package,
            self.staged_content,
            self.composition_level,
            override=False,
        )

    @patch('cms.djangoapps.import_from_modulestore.helpers.UsageKey.from_string')
    @patch('cms.djangoapps.import_from_modulestore.helpers.etree.fromstring')
    @patch('cms.djangoapps.import_from_modulestore.helpers.get_block_to_import')
    def test_import_from_staged_content_block_not_found(self, mock_get_block, mock_fromstring, mock_usage_key):
        """Test import_from_staged_content when block is not found."""
        mock_node = mock.MagicMock()
        mock_fromstring.return_value = mock_node

        mock_key = mock.MagicMock(spec=UsageKey)
        mock_usage_key.return_value = mock_key

        mock_get_block.return_value = None

        result = self.client.import_from_staged_content()

        self.assertEqual(result, [])
        mock_fromstring.assert_called_once_with(self.staged_content.olx, parser=mock.ANY)
        mock_usage_key.assert_called_once_with(self.block_usage_key)
        mock_get_block.assert_called_once_with(mock_node, mock_key)

    @patch('cms.djangoapps.import_from_modulestore.helpers.UsageKey.from_string')
    @patch('cms.djangoapps.import_from_modulestore.helpers.etree.fromstring')
    @patch('cms.djangoapps.import_from_modulestore.helpers.get_block_to_import')
    @patch('cms.djangoapps.import_from_modulestore.helpers.ImportClient._import_complicated_child')
    def test_import_from_staged_content_success(
        self, mock_import_child, mock_get_block, mock_fromstring, mock_usage_key
    ):
        """Test import_from_staged_content when block is found."""
        mock_node = mock.MagicMock()
        mock_fromstring.return_value = mock_node

        mock_key = mock.MagicMock(spec=UsageKey)
        mock_usage_key.return_value = mock_key

        mock_block = mock.MagicMock()
        mock_get_block.return_value = mock_block

        expected_result = [mock.MagicMock()]
        mock_import_child.return_value = expected_result

        result = self.client.import_from_staged_content()

        self.assertEqual(result, expected_result)
        mock_fromstring.assert_called_once_with(self.staged_content.olx, parser=mock.ANY)
        mock_usage_key.assert_called_once_with(self.block_usage_key)
        mock_get_block.assert_called_once_with(mock_node, mock_key)
        mock_import_child.assert_called_once_with(mock_block, self.block_usage_key)

    def test_should_create_container(self):
        """Test _should_create_container method."""
        # Test when container_type is not in COMPLICATED_LEVELS
        self.assertFalse(self.client._should_create_container("html"))

        # Test when composition_level is not in COMPLICATED_LEVELS
        self.client.composition_level = "html"
        self.assertFalse(self.client._should_create_container("chapter"))

        # Test when container_type is at a lower level than composition_level
        self.client.composition_level = "chapter"
        self.assertTrue(self.client._should_create_container("sequential"))
        self.assertTrue(self.client._should_create_container("vertical"))

        # Test when container_type is at a higher level than composition_level
        self.client.composition_level = "vertical"
        self.assertFalse(self.client._should_create_container("chapter"))
        self.assertFalse(self.client._should_create_container("sequential"))

        # Test when container_type is at the same level as composition_level
        self.client.composition_level = "vertical"
        self.assertTrue(self.client._should_create_container("vertical"))

    def test_can_be_container_child(self):
        """Test _can_be_container_child method."""
        # Mock child and publishable entity
        child = mock.MagicMock()
        child.tag = "chapter"

        entity = mock.MagicMock(spec=PublishableEntity)
        entity.key = "sequential.12345"

        # Test when child is a direct child of container
        self.assertTrue(self.client._can_be_container_child(child, entity))

        # Test when child is not a direct child of container
        child.tag = "vertical"
        self.assertFalse(self.client._can_be_container_child(child, entity))

        # Test when child is a sibling of container
        child.tag = "unknown"
        self.assertFalse(self.client._can_be_container_child(child, entity))

        # Test when child is a different type
        child.tag = "sequential"
        entity.key = "unknown.12345"
        self.assertFalse(self.client._can_be_container_child(child, entity))

    @patch('cms.djangoapps.import_from_modulestore.helpers.get_or_create_publishable_entity_mapping')
    def test_get_or_create_container_unknown_type(self, mock_get_or_create_mapping):
        """Test get_or_create_container with unknown container type."""
        with self.assertRaises(ValueError):
            self.client.get_or_create_container(
                "unknown_type",
                "key",
                "display_name",
                "block_usage_key_string"
            )

    @patch('cms.djangoapps.import_from_modulestore.helpers.UsageKey.from_string')
    @patch('cms.djangoapps.import_from_modulestore.helpers.get_usage_key_string_from_staged_content')
    @patch('cms.djangoapps.import_from_modulestore.helpers.ImportClient._import_child_block')
    @patch('cms.djangoapps.import_from_modulestore.helpers.ImportClient._import_simple_block')
    def test_process_import_complicated_block(
        self, mock_import_simple, mock_import_child, mock_get_key, mock_usage_key
    ):
        """Test _process_import with a complicated block."""
        mock_block = mock.MagicMock()
        mock_block.tag = "vertical"
        mock_block.getchildren.return_value = [mock.MagicMock(), mock.MagicMock()]

        mock_usage_key.return_value = mock.MagicMock(spec=UsageKey)
        mock_get_key.side_effect = ["child1_key", "child2_key"]

        expected_result = [mock.MagicMock(), mock.MagicMock()]
        mock_import_child.side_effect = [[expected_result[0]], [expected_result[1]]]

        result = self.client._process_import("test_key", mock_block)

        self.assertEqual(result, expected_result)
        self.assertEqual(mock_import_child.call_count, 2)
        mock_import_simple.assert_not_called()

    @patch('cms.djangoapps.import_from_modulestore.helpers.UsageKey.from_string')
    @patch('cms.djangoapps.import_from_modulestore.helpers.ImportClient._import_simple_block')
    def test_process_import_simple_block(self, mock_import_simple, mock_usage_key):
        """Test _process_import with a simple block."""
        mock_block = mock.MagicMock()
        mock_block.tag = "html"
        mock_block.getchildren.return_value = []

        mock_key = mock.MagicMock(spec=UsageKey)
        mock_usage_key.return_value = mock_key

        expected_result = [mock.MagicMock()]
        mock_import_simple.return_value = expected_result

        result = self.client._process_import("test_key", mock_block)

        self.assertEqual(result, expected_result)
        mock_import_simple.assert_called_once_with(mock_block, mock_key)

    @patch('cms.djangoapps.import_from_modulestore.helpers.authoring_api.create_next_container_version')
    def test_update_container_children(self, mock_create_next_version):
        """Test _update_container_children method."""
        container_version = mock.MagicMock(spec=ContainerVersion)
        container_version.container = mock.MagicMock()
        container_version.title = "Test Container"

        component_version = mock.MagicMock(spec=Component)
        component_version.component = mock.MagicMock()

        child_versions = [container_version, component_version]

        expected_result = mock.MagicMock()
        mock_create_next_version.return_value = expected_result

        result = self.client._update_container_children(container_version, child_versions)

        self.assertEqual(result, expected_result)
        mock_create_next_version.assert_called_once()
        _, kwargs = mock_create_next_version.call_args
        self.assertEqual(len(kwargs['entity_rows']), 2)

    @patch('cms.djangoapps.import_from_modulestore.helpers.authoring_api.get_components')
    @patch('cms.djangoapps.import_from_modulestore.helpers.api.library_component_usage_key')
    @patch('cms.djangoapps.import_from_modulestore.helpers.api.set_library_block_olx')
    def test_handle_component_override(self, mock_set_olx, mock_lib_usage_key, mock_get_components):
        """Test _handle_component_override method."""
        mock_component = mock.MagicMock(spec=Component)
        mock_components = mock.MagicMock()
        mock_components.get.return_value = mock_component
        mock_get_components.return_value = mock_components

        mock_usage_key = mock.MagicMock(spec=UsageKey)
        mock_usage_key.block_id = "html1"

        mock_library_usage_key = mock.MagicMock()
        mock_lib_usage_key.return_value = mock_library_usage_key

        expected_version = mock.MagicMock()
        mock_set_olx.return_value = expected_version

        result = self.client._handle_component_override(mock_usage_key, b"<html>new content</html>")

        self.assertEqual(result, expected_version)
        mock_get_components.assert_called_once_with(self.learning_package.id)
        mock_lib_usage_key.assert_called_once_with(self.client.library_key, mock_component)
        mock_set_olx.assert_called_once_with(mock_library_usage_key, b"<html>new content</html>")

    @patch('cms.djangoapps.import_from_modulestore.helpers.content_staging_api.get_staged_content_static_file_data')
    @patch('cms.djangoapps.import_from_modulestore.helpers.authoring_api.get_or_create_media_type')
    @patch('cms.djangoapps.import_from_modulestore.helpers.authoring_api.get_or_create_file_content')
    @patch('cms.djangoapps.import_from_modulestore.helpers.authoring_api.create_component_version_content')
    def test_process_staged_content_files(
        self, mock_create_version_content, mock_get_file_content, mock_get_media_type, mock_get_file_data
    ):
        """Test _process_staged_content_files method."""
        component_version = mock.MagicMock()
        component_version.pk = "component_version_pk"

        staged_content_files = [
            mock.MagicMock(filename="test_file.png"),
            mock.MagicMock(filename="not_referenced.jpg")
        ]

        mock_usage_key = mock.MagicMock(spec=UsageKey)

        mock_block = mock.MagicMock()
        mock_block_olx = b'<html>test_file.png</html>'
        etree.tostring = mock.MagicMock(return_value=mock_block_olx)

        created_at = datetime.now(timezone.utc)

        mock_file_data = b"file_data"
        mock_get_file_data.return_value = mock_file_data

        mock_media_type = mock.MagicMock()
        mock_get_media_type.return_value = mock_media_type

        mock_content = mock.MagicMock()
        mock_content.id = "content_id"
        mock_get_file_content.return_value = mock_content

        self.client._process_staged_content_files(
            component_version, staged_content_files, mock_usage_key, mock_block, created_at
        )

        mock_get_file_data.assert_called_once_with(self.staged_content.id, "test_file.png")
        mock_get_media_type.assert_called_once()
        mock_get_file_content.assert_called_once()
        mock_create_version_content.assert_called_once_with(
            component_version.pk, mock_content.id, key="static/test_file.png"
        )
# pylint: enable=protected-access
