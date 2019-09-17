from django.http import Http404
from django.shortcuts import render_to_response
from django.urls import reverse
from django.views import View
from opaque_keys.edx.keys import CourseKey

from courseware.courses import get_course_with_access
from openedx.core.djangoapps.course_groups.cohorts import is_course_cohorted


class DashboardIndex(View):
    def get(self, request, course_id, cohort_id):
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, 'instructor', course_key, depth=None)
        if not is_course_cohorted(course_key):
            raise Http404

        template_cohort_id_key = 123123123

        return render_to_response('cohort_management_dashboard/tab_index_page.html', {
            'course': course,
            'cohorts_url': reverse('cohorts', kwargs={'course_key_string': unicode(course_id)}),
            'list_cohort_url': reverse(
                'cohort_management_dashboard:all_user_list',
                kwargs={'course_id': unicode(course_id), 'cohort_id': template_cohort_id_key}
            ),
            'add_to_cohort_url': reverse(
                'add_to_cohort',
                kwargs={'course_key_string': unicode(course_id), 'cohort_id': template_cohort_id_key}
            ),
            'remove_from_cohort_url': reverse(
                'remove_from_cohort',
                kwargs={'course_key_string': unicode(course_id), 'cohort_id': template_cohort_id_key}
            ),
            'cohort_id': cohort_id,
            'template_cohort_id_key': template_cohort_id_key,
            'empty_user_list_redirect': (
                reverse('instructor_dashboard', kwargs={'course_id': unicode(course_id)}) +
                '#view-cohort_management'
            ),
            'self_page_url': reverse(
                'cohort_management_dashboard:dashboard_with_cohort',
                kwargs={'course_id': unicode(course_id), 'cohort_id': template_cohort_id_key}
            )
        })
