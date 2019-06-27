from collections import OrderedDict

from django.conf import settings
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from search.elastic import ElasticSearchEngine

from .models import CourseCategory


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
        return results
