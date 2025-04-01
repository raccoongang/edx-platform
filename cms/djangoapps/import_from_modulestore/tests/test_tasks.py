"""
Tests for tasks in import_from_modulestore app.
"""
from organizations.models import Organization

from cms.djangoapps.import_from_modulestore.data import ImportStatus
from cms.djangoapps.import_from_modulestore.tasks import (
    import_course_staged_content_to_library_task,
    save_courses_to_staged_content_task,
)
from openedx.core.djangoapps.content_libraries import api as content_libraries_api
from openedx.core.djangoapps.content_libraries.api import ContentLibrary
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
        self.content_library = ContentLibrary.objects.get_by_key(self.library.key)

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

        self.import_from_modulestore = CourseToLibraryImportFactory(
            course_ids=f'{self.course.id} {self.course2.id}',
            content_library=self.content_library,
        )
        self.user = self.import_from_modulestore.user


class TestSaveCourseSectionsToStagedContentTask(ImportCourseToLibraryMixin):
    """
    Test cases for save_course_sections_to_staged_content_task.
    """

    def test_save_courses_to_staged_content_task(self):
        """
        End-to-end test for save_courses_to_staged_content_task.
        """
        course_chapters_to_import = [self.chapter, self.chapter2]
        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        self.import_from_modulestore.refresh_from_db()
        self.assertEqual(self.import_from_modulestore.stagedcontent_set.count(), len(course_chapters_to_import))
        self.assertEqual(self.import_from_modulestore.status, ImportStatus.READY)

    def test_old_staged_content_deletion_before_save_new(self):
        """ Checking that repeated saving of the same content does not create duplicates. """
        course_ids = self.import_from_modulestore.course_id_list

        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        self.assertEqual(self.import_from_modulestore.stagedcontent_set.count(), len(course_ids))

        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        self.assertEqual(self.import_from_modulestore.stagedcontent_set.count(), len(course_ids))


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
        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        import_course_staged_content_to_library_task(
            self.user.id,
            [str(self.chapter.location), str(self.chapter2.location)],
            str(self.library.key),
            self.import_from_modulestore.uuid,
            'xblock',
            override=True
        )

        self.import_from_modulestore.refresh_from_db()
        self.assertEqual(self.import_from_modulestore.status, ImportStatus.IMPORTED)

        for xblock in expected_imported_xblocks:
            self._is_imported(self.library, xblock)
        self.assertEqual(self.library.learning_package.content_set.count(), len(expected_imported_xblocks))


    def test_import_library_block_not_found(self):
        """ Test that an error is raised if the block is not found. """
        non_existent_usage_ids = ['block-v1:edX+Demo+2023+type@vertical+block@12345']
        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        with self.assertRaises(ValueError):
            import_course_staged_content_to_library_task(
                self.user.id,
                non_existent_usage_ids,
                self.library.key,
                str(self.import_from_modulestore.uuid),
                'xblock',
                override=True,
            )
        self.assertEqual(self.library.learning_package.content_set.count(), 0)

    def test_cannot_import_staged_content_twice(self):
        """
        Tests if after importing staged content into the library,
        the staged content is deleted and cannot be imported again.
        """
        course_chapters_to_import = [self.chapter, self.chapter2]
        expected_imported_xblocks = [self.problem, self.video]
        save_courses_to_staged_content_task(self.user.id, self.import_from_modulestore.uuid)

        self.import_from_modulestore.refresh_from_db()
        self.assertEqual(self.import_from_modulestore.stagedcontent_set.count(), len(course_chapters_to_import))
        self.assertEqual(self.import_from_modulestore.status, ImportStatus.READY)

        import_course_staged_content_to_library_task(
            self.user.id,
            [str(self.chapter.location)],
            str(self.import_from_modulestore.content_library.library_key),
            str(self.import_from_modulestore.uuid),
            'xblock',
            override=True,
        )

        for xblock in expected_imported_xblocks:
            self._is_imported(self.library, xblock)
        self.assertEqual(self.library.learning_package.content_set.count(), len(expected_imported_xblocks))

        self.import_from_modulestore.refresh_from_db()
        self.assertEqual(self.import_from_modulestore.status, ImportStatus.IMPORTED)
        self.assertTrue(not self.import_from_modulestore.stagedcontent_set.exists())
