"""
Unittests for importing a library via management command
"""

import ddt
import os
from path import Path as path
import shutil
import tempfile
from StringIO import StringIO

from django.core.management import CommandError, call_command

from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import LibraryLocator
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

@ddt.ddt
class TestImportLibrary(ModuleStoreTestCase):
    """
    Unit tests for importing a library from command line
    """

    org = u'TestOrgX'
    lib_code = u'LC101'
    display_name = u'Testing Library Import'

    def create_library_xml(self, content_dir):
        directory = tempfile.mkdtemp(dir=content_dir)
        os.makedirs(os.path.join(directory, "library"))
        with open(os.path.join(directory, "library.xml"), "w+") as f:
            f.write('<library xblock-family="xblock.v1" display_name="{display_name}" org="{org}" '
                    'library="{lib_code}"/>'.format(display_name=self.display_name, org=self.org, lib_code=self.lib_code))

        return directory

    def setUp(self):
        """
        Build library XML for importing
        """
        super(TestImportLibrary, self).setUp()
        self.content_dir = path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.content_dir)

        # self.test_library = LibraryFactory.create(org=self.org, library=self.lib_code, modulestore=self.store)
        self.library_key = LibraryLocator(self.org, self.lib_code)
        self.library_dir = self.create_library_xml(self.content_dir)

    def test_library_import(self):
        """
        Try to import library
        """
        with modulestore().default_store(ModuleStoreEnum.Type.split):
            call_command('import-library', self.content_dir, self.library_dir)
            self.library_from_store = modulestore().get_library(self.library_key)

        # compare library_key of imported library with self-generated
        self.assertEqual(unicode(self.library_from_store.location.library_key), unicode(self.library_key))
        # conpare display_name of imported library with original
        self.assertEqual(unicode(self.library_from_store), u"Library: " + unicode(self.display_name))

    @ddt.data(u'/tmp/xxx/yyy/zzz', u'')
    def test_library_import_invalid_dirs(self, invalid_source_dir):
        errstring = "Imported libraries count is zero"
        with self.assertRaisesRegexp(CommandError, errstring):
            call_command('import-library', self.content_dir, invalid_source_dir)

