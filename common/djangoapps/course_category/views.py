from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from courseware.courses import get_courses
from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.theming import helpers as theming_helpers

from .models import CourseCategory


class CourseCategoryView(View):

    def get(self, request, *args, **kwargs):

        visible_courses = get_courses(request.user)
        categories = CourseCategory.objects.filter(parent=None, courses__in=visible_courses).distinct()
        context = {'categories': categories}
        return render_to_response("course_category_list.html", context)


class CategoryCoursesListView(View):

    def get(self, request, slug, *args, **kwargs):

        category = get_object_or_404(CourseCategory, slug=slug)
        courses = get_courses(request.user, filter_={'coursecategory__id': category.id})
        if not courses:
            raise Http404()
        context = {
            'category': category,
            'courses': courses,
            'courses_list': theming_helpers.get_template_path('courses_list.html')
        }
        return render_to_response("courses_list_for_category.html", context)
