"""
Cache functionality.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q

from certificates.models import GeneratedCertificate
from courseware.models import StudentModule
from student.models import UserProfile
from opaque_keys.edx.keys import UsageKey
from openedx.core.djangoapps.content.course_structures.models import CourseStructure

ACTIVE_STUDENTS_AMOUNT = 'active_students_amount'
ENTHUSIASTIC_STUDENTS = 'enthusiastic_students'
GENERATED_CERTIFICATES = 'generated_certificates'
REGISTERED_STUDENTS = 'registered_students'
STUDENTS_PER_COUNTRY = 'students_per_country'


def cache_instance_data(name_to_cache, query_type, activity_period):
    """
    Cache queries, that calculate particular instance data with week and month activity period value.

    Arguments:
        name_to_cache (str): year-week or year-month accordance as string.
        query_result (query result): Django-query result.

    Returns cached query result.
    """
    cached_query_result = cache.get(name_to_cache)

    if cached_query_result is not None:
        return cached_query_result

    query_result = get_query_result(query_type, activity_period)
    cache.set(name_to_cache, query_result)

    return query_result


def get_query_result(query_type, activity_period):
    """
    Return query result per query type.
    """
    period_start, period_end = activity_period

    if query_type == ACTIVE_STUDENTS_AMOUNT:
        return UserProfile.objects.exclude(
            Q(user__last_login=None) | Q(user__is_active=False)
        ).filter(user__last_login__gte=period_start, user__last_login__lt=period_end).count()

    if query_type == STUDENTS_PER_COUNTRY:
        return dict(
            UserProfile.objects.exclude(Q(user__last_login=None) | Q(user__is_active=False)).values(
                'country'
            ).annotate(count=Count('country')).values_list('country', 'count')
        )

    if query_type == GENERATED_CERTIFICATES:
        generated_certificates = GeneratedCertificate.objects.extra(select={'date': 'date( created_date )'}).values(
            'date'
        ).annotate(count=Count('pk'))

        return {
            certificates['date'].strftime('%Y-%m-%d'): certificates['count'] for certificates in generated_certificates
        }

    if query_type == REGISTERED_STUDENTS:
        registered_students = User.objects.exclude(is_staff=True).extra(select={'date': 'date( date_joined )'}).values(
            'date').annotate(count=Count('pk'))

        return {student['date'].strftime('%Y-%m-%d'): student['count'] for student in registered_students}

    if query_type == ENTHUSIASTIC_STUDENTS:
        # Get ordered dicts courses structure for all courses
        course_structure_query = CourseStructure.objects.all()
        courses_structures_list = [course_structure.ordered_blocks for course_structure in course_structure_query]

        last_sections_list = list()

        for course_structure in courses_structures_list:
            # Get all sections in structure
            sections = [section[1].get('usage_key', '') for section in course_structure.iteritems()]

            # Generate UsageKey for last section and add it to last_sections_list
            last_sections_list.append(UsageKey.from_string(sections[-1]))

        # Get all records from db with last sections and grouped them by date
        enthusiastic_students = StudentModule.objects.filter(module_state_key__in=last_sections_list).extra(
            select={'date': 'date( modified )'}
        ).values('date').annotate(count=Count('pk'))

        return {student['date'].strftime('%Y-%m-%d'): student['count'] for student in enthusiastic_students}


def get_cache_week_key():
    """
    Return previous week `year` and `week` numbers as unique string key for cache.
    """
    previous_week = date.today() - timedelta(days=7)
    year, week_number, _ = previous_week.isocalendar()

    return '{0}-{1}-week'.format(year, week_number)


def get_cache_month_key():
    """
    Return previous month `year` and `month` numbers as unique string key for cache.
    """
    current_month_days_count = date.today().day
    previous_month = (date.today() - timedelta(days=current_month_days_count))

    month_number = previous_month.month
    year = previous_month.year

    return '{0}-{1}-month'.format(year, month_number)
