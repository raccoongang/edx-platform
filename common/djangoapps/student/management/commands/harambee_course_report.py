from django.core.management.base import BaseCommand

from student.reports import csv_course_report


class Command(BaseCommand):
    help = 'Make harambee course report in csv format'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **options):
        with open(options['file_name'], 'wb') as csv_file:
            csv_course_report(csv_file)
