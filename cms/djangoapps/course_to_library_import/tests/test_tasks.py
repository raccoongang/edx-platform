"""
Tests for tasks in course_to_library_import app.
"""
from organizations.models import Organization
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2

from cms.djangoapps.course_to_library_import.data import CourseToLibraryImportStatus
from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport
from cms.djangoapps.course_to_library_import.tasks import (
    import_course_staged_content_to_library_task,
    save_courses_to_staged_content_task,
)
from openedx.core.djangoapps.content_libraries import api as content_libraries_api
from openedx.core.djangoapps.content_staging import api as content_staging_api
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, BlockFactory

from .factories import CourseToLibraryImportFactory


class ImportCourseToLibraryMixin(ModuleStoreTestCase):
    """
    Mixin for setting up data for tests.
    """

    def setUp(self):
        super().setUp()

        self.library = content_libraries_api.create_library(
            org=Organization.objects.create(name='Organization 1', short_name='org1'),
            slug='lib_1',
            title='Library Org 1',
            description='This is a library from Org 1',
        )

        self.course = CourseFactory.create()
        self.chapter = BlockFactory.create(category='chapter', parent=self.course, display_name='Chapter 1')
        self.sequential = BlockFactory.create(category='sequential', parent=self.chapter, display_name='Sequential 1')
        self.vertical = BlockFactory.create(category='vertical', parent=self.sequential, display_name='Vertical 1')
        self.video = BlockFactory.create(category='video', parent=self.vertical, display_name='Video 1')
        self.problem = BlockFactory.create(category='problem', parent=self.vertical, display_name='Problem 1')

        self.course2 = CourseFactory.create()
        self.chapter2 = BlockFactory.create(category='chapter', parent=self.course2, display_name='Chapter 2')
        self.sequential2 = BlockFactory.create(category='sequential', parent=self.chapter2, display_name='Sequential 2')
        self.vertical2 = BlockFactory.create(category='vertical', parent=self.sequential2, display_name='Vertical 2')
        self.video2 = BlockFactory.create(category='video', parent=self.vertical2, display_name='Video 2')
        self.problem2 = BlockFactory.create(category='problem', parent=self.vertical2, display_name='Problem 2')

        self.course_to_library_import = CourseToLibraryImportFactory(
            course_ids=f'{self.course.id} {self.course2.id}',
            library_key=str(self.library.key),
        )
        self.user_id = self.course_to_library_import.user.id
        self.purpose = 'import_from_{course_id}'



class TestSaveCourseSectionsToStagedContentTask(ImportCourseToLibraryMixin):
    """
    Test cases for save_course_sections_to_staged_content_task.
    """

    def test_save_courses_to_staged_content_task(self):
        """
        End-to-end test for save_courses_to_staged_content_task.
        """
        course_ids = self.course_to_library_import.course_ids.split(' ')
        course_chapters_count = 1

        save_courses_to_staged_content_task(
            course_ids,
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )
        course_to_library_import = CourseToLibraryImport.objects.get(id=self.course_to_library_import.id)

        for course_id in course_ids:
            ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
                self.user_id,
                self.purpose.format(course_id=course_id)
            )
            self.assertEqual(ready_staged_content.count(), course_chapters_count)

        self.assertEqual(course_to_library_import.status, CourseToLibraryImportStatus.READY)

    def test_old_staged_content_deletion_before_save_new(self):
        """ Checking that repeated saving of the same content does not create duplicates. """
        course_ids = self.course_to_library_import.course_id_list

        save_courses_to_staged_content_task(
            course_ids,
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )
        purposes = [self.purpose.format(course_id=course_id) for course_id in course_ids]
        ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id,
            purposes
        )
        self.assertEqual(ready_staged_content.count(), len(course_ids))

        save_courses_to_staged_content_task(
            course_ids,
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )
        ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id,
            purposes
        )
        self.assertEqual(ready_staged_content.count(), len(course_ids))


class TestImportLibraryFromStagedContentTask(ImportCourseToLibraryMixin):
    """
    Test cases for import_course_staged_content_to_library_task.
    """

    def _is_imported(self, library, xblock):
        self.assertTrue(library.learning_package.content_set.filter(text__icontains=xblock.display_name).exists())

    def test_import_course_staged_content_to_library_task(self):
        """ End-to-end test for import_course_staged_content_to_library_task. """
        self.assertEqual(self.library.learning_package.content_set.count(), 0)
        expected_imported_xblocks = [self.problem, self.problem2, self.video, self.video2]
        save_courses_to_staged_content_task(
            [str(self.course.id), str(self.course2.id)],
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )

        import_course_staged_content_to_library_task(
            self.user_id,
            [str(self.chapter.location), str(self.chapter2.location)],
            str(self.library.key),
            self.purpose,
            self.course_to_library_import.uuid,
            'xblock',
            override=True
        )

        self.course_to_library_import.refresh_from_db()
        self.assertEqual(self.course_to_library_import.status, CourseToLibraryImportStatus.IMPORTED)

        for xblock in expected_imported_xblocks:
            self._is_imported(self.library, xblock)
        self.assertEqual(self.library.learning_package.content_set.count(), len(expected_imported_xblocks))


    def test_import_library_block_not_found(self):
        """ Test that an error is raised if the block is not found. """
        non_existent_usage_ids = ['block-v1:edX+Demo+2023+type@vertical+block@12345']
        course_id1, course_id2 = self.course_to_library_import.course_id_list
        save_courses_to_staged_content_task(
            [course_id1, course_id2],
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )

        with self.assertRaises(ValueError):
            import_course_staged_content_to_library_task(
                self.user_id,
                non_existent_usage_ids,
                self.library.key,
                self.purpose,
                str(self.course_to_library_import.uuid),
                'xblock',
                override=True,
            )
        self.assertEqual(self.library.learning_package.content_set.count(), 0)

    def test_cannot_import_staged_content_twice(self):
        """
        Tests if after importing staged content into the library,
        the staged content is deleted and cannot be imported again.
        """
        course_id1, course_id2 = self.course_to_library_import.course_id_list
        save_courses_to_staged_content_task(
            [course_id1, course_id2],
            self.user_id,
            self.course_to_library_import.id,
            self.purpose,
        )
        expected_imported_xblocks = [self.problem, self.video]

        course_1_ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id, self.purpose.format(course_id=course_id1)
        )
        self.assertEqual(course_1_ready_staged_content.count(), 1)

        course_2_ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id, self.purpose.format(course_id=course_id2)
        )
        self.assertEqual(course_2_ready_staged_content.count(), 1)
        self.course_to_library_import.refresh_from_db()
        self.assertEqual(self.course_to_library_import.status, CourseToLibraryImportStatus.READY)

        import_course_staged_content_to_library_task(
            self.user_id,
            [str(self.chapter.location)],
            str(self.course_to_library_import.library_key),
            'import_from_{course_id}',
            str(self.course_to_library_import.uuid),
            'xblock',
            override=True,
        )

        for xblock in expected_imported_xblocks:
            self._is_imported(self.library, xblock)
        self.assertEqual(self.library.learning_package.content_set.count(), len(expected_imported_xblocks))

        self.course_to_library_import.refresh_from_db()
        self.assertEqual(self.course_to_library_import.status, CourseToLibraryImportStatus.IMPORTED)

        course_1_ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id,
            self.purpose.format(course_id=course_id1)
        )
        self.assertTrue(not course_1_ready_staged_content.exists())

        course_2_ready_staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            self.user_id,
            self.purpose.format(course_id=course_id2)
        )
        self.assertTrue(not course_2_ready_staged_content.exists())

        import_course_staged_content_to_library_task(
            self.user_id,
            [str(self.chapter2.location)],
            str(self.course_to_library_import.library_key),
            'import_from_{course_id}',
            str(self.course_to_library_import.uuid),
            'xblock',
            False,
        )
