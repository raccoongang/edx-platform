import logging
from collections import OrderedDict

from django.conf import settings
from search.elastic import ElasticSearchEngine

from .models import CourseCategory

log = logging.getLogger(__name__)

class CourseCategorySearchEngine(ElasticSearchEngine):

    def search(self, **kwargs):
        """
        Override default engine just to reorder categories
        """
        def _sort(result):
            data = result.get('data', {})
            order = data.get('order')
            return (
                order is None,
                order,
                data.get('content', {}).get('display_name'),
            )

        response = super(CourseCategorySearchEngine, self).search(**kwargs)
        if not response:
            log.warning('Something wrong with "edx_search engine", nothing to sort!')
            return {}
        response.get('results', []).sort(key=_sort)
        return response
