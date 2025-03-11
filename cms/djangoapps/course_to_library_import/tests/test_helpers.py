"""
Tests for the course_to_library_import helper functions.
"""

from unittest import mock
from lxml import etree
from django.test import TestCase
from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2, LibraryUsageLocatorV2

from cms.djangoapps.course_to_library_import.helpers import create_block_in_library, flat_import_children
from common.djangoapps.student.tests.factories import UserFactory


class TestFlatImportChildren(TestCase):
    """
    Tests for the flat_import_children helper function.
    """

    def setUp(self):
        super().setUp()
        self.library_key = LibraryLocatorV2(org="TestOrg", slug="test-lib")
        self.user_id = "test_user"

        # Create mock staged content
        self.staged_content = mock.MagicMock()
        self.staged_content.id = "staged-content-id"
        self.staged_content.tags = {
            "block-v1:TestOrg+TestCourse+Run1+type@problem+block@problem1": {},
            "block-v1:TestOrg+TestCourse+Run1+type@html+block@html1": {},
            "block-v1:TestOrg+TestCourse+Run1+type@video+block@video1": {},
        }

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.create_block_in_library')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_flat_import_children_basic(self, mock_content_library, mock_create_block):
        # Create a simple XML structure with one vertical and two children
        xml = """
        <vertical url_name="vertical1">
            <problem url_name="problem1"/>
            <html url_name="html1"/>
        </vertical>
        """
        block_to_import = etree.fromstring(xml)

        # Mock library objects
        mock_library = mock.MagicMock()
        mock_content_library.objects.filter.return_value.first.return_value = mock_library

        # Call the function
        flat_import_children(block_to_import, self.library_key, self.user_id, self.staged_content, False)

        # Verify create_block_in_library was called twice (for problem1 and html1)
        self.assertEqual(mock_create_block.call_count, 2)

        # Check the calls to create_block_in_library
        usage_key_problem = UsageKey.from_string("block-v1:TestOrg+TestCourse+Run1+type@problem+block@problem1")
        usage_key_html = UsageKey.from_string("block-v1:TestOrg+TestCourse+Run1+type@html+block@html1")

        mock_create_block.assert_any_call(
            mock.ANY, usage_key_problem, self.library_key, self.user_id, self.staged_content.id, False
        )
        mock_create_block.assert_any_call(
            mock.ANY, usage_key_html, self.library_key, self.user_id, self.staged_content.id, False
        )

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.create_block_in_library')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_flat_import_children_nested_structure(self, mock_content_library, mock_create_block):
        # Create a nested XML structure
        xml = """
        <chapter url_name="chapter1">
            <sequential url_name="sequential1">
                <vertical url_name="vertical1">
                    <problem url_name="problem1"/>
                    <html url_name="html1"/>
                </vertical>
            </sequential>
        </chapter>
        """
        block_to_import = etree.fromstring(xml)

        # Mock library objects
        mock_library = mock.MagicMock()
        mock_content_library.objects.filter.return_value.first.return_value = mock_library

        # Call the function
        flat_import_children(block_to_import, self.library_key, self.user_id, self.staged_content, False)

        # Verify create_block_in_library was called twice (for problem1 and html1)
        self.assertEqual(mock_create_block.call_count, 2)

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.create_block_in_library')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_flat_import_children_with_override(self, mock_content_library, mock_create_block):
        xml = """
        <vertical url_name="vertical1">
            <problem url_name="problem1"/>
        </vertical>
        """
        block_to_import = etree.fromstring(xml)

        # Mock library objects
        mock_library = mock.MagicMock()
        mock_content_library.objects.filter.return_value.first.return_value = mock_library

        # Call the function with override=True
        flat_import_children(block_to_import, self.library_key, self.user_id, self.staged_content, True)

        # Verify create_block_in_library was called with override=True
        usage_key_problem = UsageKey.from_string("block-v1:TestOrg+TestCourse+Run1+type@problem+block@problem1")
        mock_create_block.assert_called_with(
            mock.ANY, usage_key_problem, self.library_key, self.user_id, self.staged_content.id, True
        )

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_flat_import_children_library_not_found(self, mock_content_library):
        xml = """
        <vertical url_name="vertical1">
            <problem url_name="problem1"/>
        </vertical>
        """
        block_to_import = etree.fromstring(xml)

        # Mock library not found
        mock_content_library.objects.filter.return_value.first.return_value = None

        # Should raise ValueError when library not found
        with self.assertRaises(ValueError):
            flat_import_children(block_to_import, self.library_key, self.user_id, self.staged_content, False)

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.create_block_in_library')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_flat_import_children_ignores_unmatched_url_names(self, mock_content_library, mock_create_block):
        xml = """
        <vertical url_name="vertical1">
            <problem url_name="problem_not_in_staged_content"/>
        </vertical>
        """
        block_to_import = etree.fromstring(xml)

        # Mock library objects
        mock_library = mock.MagicMock()
        mock_content_library.objects.filter.return_value.first.return_value = mock_library

        # Call the function
        flat_import_children(block_to_import, self.library_key, self.user_id, self.staged_content, False)

        # Verify create_block_in_library was not called (url_name not in staged content)
        mock_create_block.assert_not_called()


class TestCreateBlockInLibrary(TestCase):
    """
    Tests for the create_block_in_library helper function.
    """

    def setUp(self):
        super().setUp()
        self.library_key = LibraryLocatorV2(org="TestOrg", slug="test-lib")
        self.user_id = UserFactory().id
        self.staged_content_id = "staged-content-id"

        self.block_xml = """<problem url_name="problem1">
            <p>What is 1+1?</p>
            <choiceresponse>
                <checkboxgroup label="Select the correct answer">
                    <choice correct="true">2</choice>
                    <choice correct="false">3</choice>
                </checkboxgroup>
            </choiceresponse>
        </problem>"""
        self.block_to_import = etree.fromstring(self.block_xml)
        self.usage_key = UsageKey.from_string("block-v1:TestOrg+TestCourse+Run1+type@problem+block@problem1")
        self.library_usage_key = LibraryUsageLocatorV2(
            lib_key=self.library_key,
            block_type="problem",
            usage_id="problem1"
        )

        # Mock the content library
        self.mock_library = mock.MagicMock()
        self.mock_library.learning_package.id = "test-package-id"
        self.mock_library.org.short_name = "TestOrg"
        self.mock_library.slug = "test-lib"

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.content_staging_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.authoring_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.CourseToLibraryImport')
    def test_create_block_in_library_new_component(
            self, mock_course_import,
            mock_content_library, mock_authoring_api, mock_api, mock_staging_api
    ):
        # Setup mocks
        mock_content_library.objects.get_by_key.return_value = self.mock_library
        mock_authoring_api.get_or_create_component_type.return_value = "problem-type"
        mock_authoring_api.get_components.return_value.filter.return_value.exists.return_value = False
        mock_api.validate_can_add_block_to_library.return_value = (None, self.library_usage_key)
        mock_component_version = mock.MagicMock()
        mock_api.set_library_block_olx.return_value = mock_component_version
        mock_staging_api.get_staged_content_static_files.return_value = []
        mock_course_import.objects.get.return_value = mock.MagicMock()

        # Call the function
        create_block_in_library(
            self.block_to_import, self.usage_key, self.library_key, self.user_id, self.staged_content_id, False
        )

        # Verify the expected API calls
        mock_authoring_api.get_or_create_component_type.assert_called_once_with("xblock.v1", "problem")
        mock_authoring_api.get_components.assert_called_once()
        mock_api.validate_can_add_block_to_library.assert_called_once_with(
            self.library_key, "problem", "problem1"
        )
        mock_authoring_api.create_component.assert_called_once_with(
            self.mock_library.learning_package.id,
            component_type="problem-type",
            local_key="problem1",
            created=mock.ANY,
            created_by=self.user_id,
        )
        mock_api.set_library_block_olx.assert_called_once_with(
            self.library_usage_key, etree.tostring(self.block_to_import)
        )

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.content_staging_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.authoring_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.log')
    def test_create_block_in_library_existing_component_no_override(
            self, mock_log, mock_content_library, mock_authoring_api, mock_api, mock_staging_api
    ):
        # Setup mocks
        mock_content_library.objects.get_by_key.return_value = self.mock_library
        mock_authoring_api.get_or_create_component_type.return_value = "problem-type"
        mock_authoring_api.get_components.return_value.filter.return_value.exists.return_value = True

        # Call the function
        create_block_in_library(
            self.block_to_import, self.usage_key, self.library_key, self.user_id, self.staged_content_id, False
        )

        # Verify that component creation was skipped
        mock_log.warning.assert_called_once()
        mock_authoring_api.create_component.assert_not_called()
        mock_api.set_library_block_olx.assert_not_called()

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.content_staging_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.authoring_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.CourseToLibraryImport')
    def test_create_block_in_library_with_override(
            self, mock_course_import,
            mock_content_library, mock_authoring_api, mock_api, mock_staging_api
    ):
        # Setup mocks
        mock_content_library.objects.get_by_key.return_value = self.mock_library
        mock_authoring_api.get_or_create_component_type.return_value = "problem-type"
        mock_authoring_api.get_components.return_value.filter.return_value.exists.return_value = True
        mock_api.validate_can_add_block_to_library.return_value = (None, self.library_usage_key)
        mock_component_version = mock.MagicMock()
        mock_api.set_library_block_olx.return_value = mock_component_version
        mock_staging_api.get_staged_content_static_files.return_value = []
        mock_course_import.objects.get.return_value = mock.MagicMock()
        mock_publishable_entity = mock.MagicMock()
        mock_authoring_api.get_publishable_entity_by_key.return_value = mock_publishable_entity

        # Call the function with override=True
        create_block_in_library(
            self.block_to_import, self.usage_key, self.library_key, self.user_id, self.staged_content_id, True
        )

        # Verify that the component was deleted and recreated
        mock_authoring_api.get_publishable_entity_by_key.assert_called_once_with(
            self.mock_library.learning_package.id, "xblock.v1:problem:problem1"
        )
        mock_publishable_entity.delete.assert_called_once()
        mock_api.validate_can_add_block_to_library.assert_called_once()
        mock_authoring_api.create_component.assert_called_once()
        mock_api.set_library_block_olx.assert_called_once()

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.content_staging_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.authoring_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ComponentVersionImport')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.CourseToLibraryImport')
    def test_create_block_in_library_with_static_files(
            self, mock_course_import, mock_component_version_import,
            mock_content_library, mock_authoring_api, mock_api, mock_staging_api
    ):
        # Setup mocks
        mock_content_library.objects.get_by_key.return_value = self.mock_library
        mock_authoring_api.get_or_create_component_type.return_value = "problem-type"
        mock_authoring_api.get_components.return_value.filter.return_value.exists.return_value = False
        mock_api.validate_can_add_block_to_library.return_value = (None, self.library_usage_key)
        mock_component_version = mock.MagicMock()
        mock_api.set_library_block_olx.return_value = mock_component_version
        mock_course_import.objects.get.return_value = mock.MagicMock()

        # Mock static files
        mock_file_data = mock.MagicMock()
        mock_file_data.filename = "image.jpg"
        mock_staging_api.get_staged_content_static_files.return_value = [mock_file_data]
        mock_staging_api.get_staged_content_static_file_data.return_value = b"file_content"

        # Update block XML to reference the file
        block_xml_with_image = """<problem url_name="problem1">
            <p>What is 1+1? <img src="image.jpg" /></p>
            <choiceresponse>
                <checkboxgroup label="Select the correct answer">
                    <choice correct="true">2</choice>
                    <choice correct="false">3</choice>
                </checkboxgroup>
            </choiceresponse>
        </problem>"""
        block_with_image = etree.fromstring(block_xml_with_image)

        # Mock media type
        mock_media_type = mock.MagicMock()
        mock_authoring_api.get_or_create_media_type.return_value = mock_media_type

        # Mock file content
        mock_file_content = mock.MagicMock()
        mock_authoring_api.get_or_create_file_content.return_value = mock_file_content

        # Call the function
        create_block_in_library(
            block_with_image, self.usage_key, self.library_key, self.user_id, self.staged_content_id, False
        )

        # Verify file processing
        mock_staging_api.get_staged_content_static_file_data.assert_called_once_with(
            self.staged_content_id, "image.jpg"
        )
        mock_authoring_api.get_or_create_media_type.assert_called_once()
        mock_authoring_api.get_or_create_file_content.assert_called_once_with(
            self.mock_library.learning_package.id,
            mock_media_type.id,
            data=b"file_content",
            created=mock.ANY
        )
        mock_authoring_api.create_component_version_content.assert_called_once_with(
            mock_component_version.pk,
            mock_file_content.id,
            key=f"static/{self.usage_key}"
        )

    @mock.patch('cms.djangoapps.course_to_library_import.helpers.content_staging_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.authoring_api')
    @mock.patch('cms.djangoapps.course_to_library_import.helpers.ContentLibrary')
    def test_create_block_in_library_file_not_referenced(
            self, mock_content_library, mock_authoring_api, mock_api, mock_staging_api
    ):
        # Setup mocks
        mock_content_library.objects.get_by_key.return_value = self.mock_library
        mock_authoring_api.get_or_create_component_type.return_value = "problem-type"
        mock_authoring_api.get_components.return_value.filter.return_value.exists.return_value = False
        mock_api.validate_can_add_block_to_library.return_value = (None, self.library_usage_key)
        mock_component_version = mock.MagicMock()
        mock_api.set_library_block_olx.return_value = mock_component_version

        # Mock static files with a file not referenced in the block
        mock_file_data = mock.MagicMock()
        mock_file_data.filename = "unused_image.jpg"
        mock_staging_api.get_staged_content_static_files.return_value = [mock_file_data]
        mock_staging_api.get_staged_content_static_file_data.return_value = b"file_content"

        # Call the function
        create_block_in_library(
            self.block_to_import, self.usage_key, self.library_key, self.user_id, self.staged_content_id, False
        )

        # The file content should not be created since it's not referenced in the block
        mock_authoring_api.get_or_create_file_content.assert_not_called()
        mock_authoring_api.create_component_version_content.assert_not_called()
