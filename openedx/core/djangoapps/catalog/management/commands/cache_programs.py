import logging
import sys

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.management import BaseCommand

from course_category.models import Program
from openedx.core.djangoapps.catalog.cache import (
    PROGRAM_CACHE_KEY_TPL,
    SITE_PROGRAM_UUIDS_CACHE_KEY_TPL
)
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.catalog.utils import create_catalog_api_client, get_programs

logger = logging.getLogger(__name__)
User = get_user_model()  # pylint: disable=invalid-name


class Command(BaseCommand):
    """Management command used to cache program data.

    This command requests every available program from the discovery
    service, writing each to its own cache entry with an indefinite expiration.
    It is meant to be run on a scheduled basis and should be the only code
    updating these cache entries.
    """
    help = "Rebuild the LMS' cache of program data."

    def handle(self, *args, **options):
        failure = False
        logger.info('populate-multitenant-programs switch is ON')

        catalog_integration = CatalogIntegration.current()
        username = catalog_integration.service_username

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error(
                'Failed to create API client. Service user {username} does not exist.'.format(username=username)
            )
            raise

        programs = {}
        for site in Site.objects.all():
            site_config = getattr(site, 'configuration', None)
            if site_config is None or not site_config.get_value('COURSE_CATALOG_API_URL'):
                logger.info('Skipping site {domain}. No configuration.'.format(domain=site.domain))
                cache.set(SITE_PROGRAM_UUIDS_CACHE_KEY_TPL.format(domain=site.domain), [], None)
                continue

            client = create_catalog_api_client(user, site=site)
            uuids, program_uuids_failed = self.get_site_program_uuids(client, site)
            new_programs, program_details_failed = self.fetch_program_details(client, uuids)

            if program_uuids_failed or program_details_failed:
                failure = True

            programs.update(new_programs)

            logger.info('Caching UUIDs for {total} programs for site {site_name}.'.format(
                total=len(uuids),
                site_name=site.domain,
            ))
            cache.set(SITE_PROGRAM_UUIDS_CACHE_KEY_TPL.format(domain=site.domain), uuids, None)

        successful = len(programs)
        logger.info('Caching details for {successful} programs.'.format(successful=successful))
        cache.set_many(programs, None)

        self.update_db_programs()

        if failure:
            # This will fail a Jenkins job running this command, letting site
            # operators know that there was a problem.
            sys.exit(1)

    def get_site_program_uuids(self, client, site):
        failure = False
        uuids = []
        try:
            querystring = {
                'exclude_utm': 1,
                'status': ('active', 'retired'),
                'uuids_only': 1,
            }

            logger.info('Requesting program UUIDs for {domain}.'.format(domain=site.domain))
            uuids = client.programs.get(**querystring)
        except:  # pylint: disable=bare-except
            logger.error('Failed to retrieve program UUIDs for site: {domain}.'.format(domain=site.domain))
            failure = True

        logger.info('Received {total} UUIDs for site {domain}'.format(
            total=len(uuids),
            domain=site.domain
        ))
        return uuids, failure

    def fetch_program_details(self, client, uuids):
        programs = {}
        failure = False
        for uuid in uuids:
            try:
                cache_key = PROGRAM_CACHE_KEY_TPL.format(uuid=uuid)
                logger.info('Requesting details for program {uuid}.'.format(uuid=uuid))
                program = client.programs(uuid).get(exclude_utm=1)
                programs[cache_key] = program
            except:  # pylint: disable=bare-except
                logger.exception('Failed to retrieve details for program {uuid}.'.format(uuid=uuid))
                failure = True
                continue
        return programs, failure

    def update_db_programs(self):
        site = Site.objects.get_current()
        pms = get_programs(site)

        current_programs = [p for p in Program.objects.values_list('uuid', flat=True)]

        for i in range(len(pms)):
            program = pms[i]
            uuid = program.get('uuid')
            title = program.get('title')
            subtitle = program.get('subtitle')
            courses = list()

            program_courses = program.get('courses')
            for program_course in program_courses:
                course_runs = program_course.get('course_runs')

                for course_run in course_runs:
                    courses.append(course_run)


            if uuid not in current_programs:
                Program.objects.create(uuid=uuid, title=title, subtitle=subtitle, courses=courses)

            else:
                existing_program = Program.objects.get(uuid=uuid)

                if existing_program.title != title:
                    existing_program.title = title

                if existing_program.subtitle != subtitle:
                    existing_program.subtitle = subtitle

                existing_program.courses = courses

                existing_program.save()

        for current_program in current_programs:
            if current_program not in [pm['uuid'] for pm in pms]:
                Program.objects.filter(uuid=current_program).delete()
