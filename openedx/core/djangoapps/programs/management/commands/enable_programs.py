import logging

from django.contrib.sites.models import Site
from django.core.management import BaseCommand
from django.core.management.base import CommandError

from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration

logger = logging.getLogger(__name__)


def set_current_config(cls, args):
    """
    Check and update config if it isn't up to date with passed args.

    Args:
        cls (ConfigurationModel): configuration model for wich checking is performed.
        args (dict): model fields values to compate with.
    """
    if not cls.equal_to_current(args):
        logger.info('Updating {} with args: {}'.format(cls.__name__, args))
        config = cls(**args)
        config.save()
    else:
        logger.info('{} is up to date, skipping...'.format(cls.__name__))


class Command(BaseCommand):
    """
    Set up programs configurations for the LMS.

    Example usage:
        ./manage.py lms enable_programs --site-domain=example.com --discovery-api-url=http://edx.devstack.discovery:18381/api/v1/ --settings=production
        ./manage.py lms enable_programs --site-domain=example.com --discovery-api-url=http://edx.devstack.discovery:18381/api/v1/ --service-username=discovery_worker --settings=production
    """
    help = 'Create or update LMS configuration models to enable programs feature.'

    def add_arguments(self, parser):
        parser.add_argument('--site-domain',
                            action='store',
                            dest='site_domain',
                            type=str,
                            required=True,
                            help='Site domain, e.g. example.com')
        parser.add_argument('--discovery-api-url',
                            action='store',
                            dest='discovery_api_url',
                            type=str,
                            required=True,
                            help='Discovery API URL, e.g. http://edx.devstack.discovery:18381/api/v1/.')
        parser.add_argument('--service-username',
                            action='store',
                            dest='service_username',
                            type=str,
                            default='discovery_worker',
                            help='Discovery service user, e.g. discovery_worker.')

    def handle(self, *args, **options):
        domain = options.get('site_domain')
        discovery_api_url = options.get('discovery_api_url')
        service_username = options.get('service_username')

        # Enable the program dashboard
        set_current_config(ProgramsApiConfig, {'enabled': True})

        # Enable the discovery worker
        set_current_config(CatalogIntegration, {
            'enabled': True,
            # `internal_api_url` is depricated and has no use across the platform, but required in model validation
            'internal_api_url': discovery_api_url,
            'service_username': service_username,
        })

        # Tell LMS about discovery
        try:
            site = Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            raise CommandError(
                'Failed to get site with domain [{}]. Site configuration was not updated.'.format(domain)
            )

        site_configuration, created = SiteConfiguration.objects.get_or_create(site=site)
        if created:
            logger.info(
                "Site configuration does not exist. Created new instance for '{site_name}'".format(
                    site_name=site.domain
                )
            )
            site_configuration.site_values = {'COURSE_CATALOG_API_URL': discovery_api_url}
        else:
            logger.info(
                "Found existing site configuration for '{site_name}'. Updating it.".format(site_name=site.domain)
            )
            if site_configuration.site_values:
                if site_configuration.site_values.get('COURSE_CATALOG_API_URL'):
                    logger.info(
                        "COURSE_CATALOG_API_URL was already set for '{site_name}' site configurations."
                        " Skipping...".format(site_name=site.domain)
                    )
                else:
                    site_configuration.site_values.update({'COURSE_CATALOG_API_URL': discovery_api_url})
            else:
                site_configuration.site_values = {'COURSE_CATALOG_API_URL': discovery_api_url}

        site_configuration.enabled = True
        site_configuration.save()

        self.stdout.write(self.style.SUCCESS('Successfully processed programs configurations update.'))
