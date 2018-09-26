from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django_countries import countries


class Command(BaseCommand):
    """
    Management command which left students active only if they are from the certain country.
    """

    help = 'Sift (deactivate) students if they are not from the chosen country.'

    def add_arguments(self, parser):
        parser.add_argument('country')

    @transaction.atomic
    def handle(self, country, *args, **options):
        country_id = countries.by_name(country.title())
        if not country_id:
            self.stderr.write(
                "Unfortunately the country {} cannot be recognized. Please check the input country value."
            )
        else:
            self.stdout.write("Student not from the {} will be deactivated.".format(country))
            for user in get_user_model().objects.exclude(profile__country=country_id):
                if hasattr(user, 'profile') and not user.is_staff:
                    user.is_active = False
                    user.save()
                    self.stdout.write("Student {} is deactivated.".format(user.username))
