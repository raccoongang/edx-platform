from collections import OrderedDict

from django.conf import settings
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from search.elastic import ElasticSearchEngine

from .models import CourseCategory, Program


class CourseCategorySearchEngine(ElasticSearchEngine):

    def search(self, **kwargs):
        """
        Override default engine just to reorder categories
        """
        results = super(CourseCategorySearchEngine, self).search(**kwargs)

        if 'category' in settings.COURSE_DISCOVERY_FILTERS:
            categories = CourseCategory.objects.filter(parent=None).exclude(courses=CourseKeyField.Empty)
            facets_category_terms = results.get('facets', {}).get('category', {}).get('terms')
            if facets_category_terms:
                terms = OrderedDict()
                for category in categories:
                    if facets_category_terms.get(category.name):
                        terms[category.name] = facets_category_terms.get(category.name)
                results['facets']['category']['terms'] = terms
        programs = _search_programs(**kwargs)
        courses = list(results.get('results', []))
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
        courses_ids = [course.get('data', {}).get('id') for course in courses]
        ungrouped_courses_ids = set(courses_ids) - already_grouped_courses_ids

        if ungrouped_courses_ids:
            ungrouped_courses = list(filter(lambda c: c.get('data', {}).get('id') in ungrouped_courses_ids, courses))
            programs.append({
                'title': 'Without program',
                'subtitle': '',
                'courses': ungrouped_courses
            })
        results['programs'] = programs
        return results

def _search_programs(**kwargs):

    title = kwargs.get('query_string', '')

    if title:
        title_qs_for_program_title = Program.objects.filter(title__icontains=title)
        title_qs_for_program_subtitle = Program.objects.filter(subtitle__icontains=title)
        title_qs = title_qs_for_program_title | title_qs_for_program_subtitle
    else:
        title_qs = Program.objects.all()

    category = kwargs.get('field_dictionary', {}).get('category', '')

    if category:
        category_qs = Program.objects.filter(coursecategory__name__iexact=category)
    else:
        category_qs = Program.objects.all()

    result_intersection = title_qs & category_qs

    result = [{'title':p.title, 'subtitle':p.subtitle, 'courses':p.courses} for p in result_intersection]

    return result
