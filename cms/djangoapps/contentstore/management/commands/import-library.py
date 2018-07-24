"""
Script for importing library content from XML format
"""
import os

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django_comment_common.utils import are_permissions_roles_seeded, seed_permissions_roles

from xmodule.contentstore.django import contentstore
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_importer import import_library_from_xml


class Command(BaseCommand):
    """
    Import the specified library data directory into the default ModuleStore
    """
    help = """
    Import the specified library(s) data directory into the default ModuleStore

    Usage: cms import-library <data_directory> [--nostatic] <library_dir> [<library_dir>...]
    data_directory - usually /edx/var/edxapp/data
    library_dir - unpacked archive, obtained via `CMS - Library - Export` interface
    directory and its content must be readable by www-data user
    """

    option_list = BaseCommand.option_list + (
        make_option('--nostatic',
                    action='store_true',
                    help='Skip import of static content'),
    )

    def handle(self, *args, **options):
        """
        Execute the command
        """
        do_import_static = not options.get('nostatic', False)
        if len(args) < 2:
            raise CommandError("ERROR: import-library requires at least two arguments: <data_directory> [--nostatic] <library_dir> [<library_dir>...]")

        data_dir = args[0]
        if len(args) > 1:
            source_dirs = args[1:]
        else:
            raise CommandError("ERROR: import-library requires at least one library_dir as argument")

        self.stdout.write("Importing.  Data_dir={data}, source_dirs={courses}\n".format(
            data=data_dir,
            courses=source_dirs,
        ))

        course_items = import_library_from_xml(
            modulestore(), ModuleStoreEnum.UserID.mgmt_command, data_dir, source_dirs, load_error_modules=False,
            static_content_store=contentstore(), verbose=True,
            do_import_static=do_import_static,
            create_if_not_present=True,
        )

        if course_items:
            self.stdout.write("Successfully imported {} libraries.\n".format(len(course_items)))
        else:
            raise CommandError("ERROR: Imported libraries count is zero! Check log for errors.\n")
