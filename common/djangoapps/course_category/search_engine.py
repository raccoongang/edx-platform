from collections import OrderedDict

from django.conf import settings
from django.db.models import (
    Count,
    Q,
)

from search.elastic import ElasticSearchEngine

from .models import CourseCategory, Program


class CourseCategorySearchEngine(ElasticSearchEngine):

    def search(self, **kwargs):
        """
        Override default engine just to reorder categories
        """
        results = super(CourseCategorySearchEngine, self).search(**kwargs)

        programs = _search_programs(**kwargs)

        if 'category' in settings.COURSE_DISCOVERY_FILTERS:
            programs_uuids = [program.uuid for program in programs]
            programs_categories = CourseCategory.objects.filter(
                parent=None, programs__uuid__in=programs_uuids,
            ).annotate(programs_count=Count('programs'))

            programs_category_terms = {
                category.name: category.programs_count for category in programs_categories
            }

            courses_category_terms = results.get('facets', {}).get('category', {}).get('terms')
            courses_facets_total_terms = results.get('facets', {}).get('category', {}).get('total')

            facets_category_terms = dict()
            for category_term in set(courses_category_terms.keys() + programs_category_terms.keys()):
                courses_term_count = courses_category_terms.get(category_term, 0)
                programs_term_count = programs_category_terms.get(category_term, 0)

                facets_category_terms[category_term] = courses_term_count + programs_term_count

            if facets_category_terms:
                terms = OrderedDict()
                categories = CourseCategory.objects.filter(parent=None).exclude(courses=None, programs=None)

                for category in categories:
                    facet_term = facets_category_terms.get(category.name)

                    if facet_term:
                        terms[category.name] = facet_term

                results['facets']['category']['terms'] = terms
                results['facets']['category']['total'] = courses_facets_total_terms

        courses = list(results.get('results', []))
        programs = _format_programs(programs)

        results['programs_total'] = len(programs)
        results['programs'] = _replace_courses_with_elastic_data(programs, courses)

        return results


def _replace_courses_with_elastic_data(programs, courses):
    """
    Replace courses with elastic data.

    Arguments:
        programs(list(dict)): A list of programs data retrieved from cache.
        courses(list(dict)): A list of all courses retrieved from Elastic search.

    Returns:
        dict: A list of programs data with all courses replaced with
              corresponding courses data from elastic search.
    """
    already_grouped_courses_ids = set()

    for program in programs:
        program_courses = program.get('courses')
        elastics_program_courses = list()

        for course in courses:
            course_data = course.get('data')

            for program_course in program_courses:
                if course_data.get('id') == program_course.get('key'):
                    elastics_program_courses.append(course)
                    already_grouped_courses_ids.add(course_data.get('id'))

                    break

        program['courses'] = elastics_program_courses

    return _group_ungrouped_courses(programs, courses, already_grouped_courses_ids)


def _group_ungrouped_courses(programs, courses, already_grouped_courses_ids):
    """
    Group ungrouped courses into a fictional group `Without group`.

    Arguments:
        programs(list(dict)): A list of programs.
        courses(list(dict)): A list of all courses retrieved from Elastic search.
        already_grouped_courses_ids(set): A list of already grouped courses ids.

    Returns:
        dict: A dictionary of programs data with extra `Without group` program
              in case `courses` contains courses that does not belong to any program.
    """
    courses_ids = [c.get('data', {}).get('id') for c in courses if c.get('data', {}).get('id') is not None]
    ungrouped_courses_ids = set(courses_ids) - already_grouped_courses_ids

    if ungrouped_courses_ids:
        ungrouped_courses = [course for course in courses if course.get('data', {}).get('id') in ungrouped_courses_ids]

        programs.append({
            'title': 'Without program',
            'subtitle': '',
            'courses': ungrouped_courses
        })

    return programs


def _search_programs(**kwargs):
    query_string = kwargs.get('query_string', '')

    search_results = Program.objects.all()

    if query_string:
        search_results = search_results.filter(Q(title__icontains=query_string) | Q(subtitle__icontains=query_string))

    category = kwargs.get('field_dictionary', {}).get('category', '')

    if category:
        search_results = search_results.filter(coursecategory__name__iexact=category)

    return search_results


def _format_programs(programs):
    """
    Format programs list.

    Each program data is presented according to the scheme:
        {
            'title': ...,
            'subtitle': ...,
            'courses': [...]
        }

    Arguments:
        programs (list(Program)): A list of Program model objects.

    Returns:
        list(dict): A formatted list of programs as dictionary data.
    """
    return [{'title': p.title, 'subtitle': p.subtitle, 'courses': p.courses} for p in programs]
