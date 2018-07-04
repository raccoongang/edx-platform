from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Enroll students in their relevant programs'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        """
        print "Hello world"
