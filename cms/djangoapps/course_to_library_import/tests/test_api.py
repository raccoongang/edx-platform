"""
Test cases for course_to_library_import.api module.
"""

from unittest.mock import patch

import pytest

from common.djangoapps.student.tests.factories import UserFactory
from cms.djangoapps.course_to_library_import.api import create_import, import_course_staged_content_to_library
from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport
from openedx.core.djangoapps.content_libraries.tests.factories import ContentLibraryFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from .factories import CourseToLibraryImportFactory


@pytest.mark.django_db
class TestCourseToLibraryImportAPI(ModuleStoreTestCase):
    """
    Test cases for CourseToLibraryImport API.
    """

    def setUp(self):
        super().setUp()

        self.library = ContentLibraryFactory()

    def test_create_import(self):
        """
        Test create_import function.
        """
        course_ids = ["course-v1:edX+DemoX+Demo_Course", "course-v1:edX+DemoX+Demo_Course_2"]
        user = UserFactory()
        with patch(
            "cms.djangoapps.course_to_library_import.api.save_courses_to_staged_content_task"
        ) as save_courses_to_staged_content_task_mock:
            create_import(course_ids, user.id, str(self.library.library_key))

        course_to_library_import = CourseToLibraryImport.objects.get()
        assert course_to_library_import.course_ids == " ".join(course_ids)
        assert course_to_library_import.content_library.library_key == self.library.library_key
        assert course_to_library_import.user_id == user.id
        save_courses_to_staged_content_task_mock.delay.assert_called_once_with(user.id, course_to_library_import.uuid)

    def test_import_course_staged_content_to_library(self):
        """
        Test import_course_staged_content_to_library function with different override values.
        """
        ctli = CourseToLibraryImportFactory()
        library_key = ctli.content_library.library_key
        usage_ids = [
            "block-v1:edX+DemoX+Demo_Course+type@html+block@123",
            "block-v1:edX+DemoX+Demo_Course+type@html+block@456",
        ]
        override = False

        with patch(
            "cms.djangoapps.course_to_library_import.api.import_course_staged_content_to_library_task"
        ) as import_course_staged_content_to_library_task_mock:
            import_course_staged_content_to_library(library_key, ctli.user.id, usage_ids, ctli.uuid, 'xblock', override)

        import_course_staged_content_to_library_task_mock.delay.assert_called_once_with(
            ctli.user.id, usage_ids, library_key, ctli.uuid, 'xblock', override
        )
