"""
View which retrieve hera onboarding pages and handle user onboarding states.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect, Http404
from django.views.generic import View
from django.urls import reverse
from django.utils.decorators import method_decorator

from edxmako.shortcuts import render_to_response
from lms.djangoapps.courseware.views.views import CourseTabView

from hera.models import Onboarding, UserOnboarding, ActiveCourseSetting
from hera.fragments import SelectionPageOutlineFragmentView, DashboardPageOutlineFragmentView
from openedx.features.course_experience.views.course_home import CourseHomeFragmentView, CourseHomeView


@method_decorator(login_required, name='dispatch')
class OnboardingPagesView(View):
    """
    Represent user onboarding pages and handle it.
    """

    def get(self, request, **kwargs):
        """
        Render user onboarding pages.
        """
        user_onboarding, _ = UserOnboarding.objects.get_or_create(user=request.user)
        if user_onboarding.is_passed():
            return HttpResponseRedirect('/')
        context = {
            'pages': user_onboarding.get_pages(),
            'current_page': user_onboarding.get_current_page(),
            'is_passed': user_onboarding.is_passed(),
        }
        return render_to_response("hera/onboarding.html", context)

    def post(self, request, **kwargs):
        """
        Save user onboarding pages status.
        """
        page = request.POST.get('page')
        if request.is_ajax() and page:
            user_onboarding = UserOnboarding.update(self.request.user, page)
            return JsonResponse({
                'success': True,
                'next_page': user_onboarding.get_next_page(page),
                'current_page': page,
                'is_passed': user_onboarding.is_passed(),
            })
        return HttpResponseForbidden()


class SelectionPageFragmentView(CourseHomeFragmentView):
    outline_fragment_view = SelectionPageOutlineFragmentView


class SelectionPageView(CourseHomeView):
    """
    The home page for the first two lessons
    """

    def render_to_fragment(self, request, course=None, tab=None, **kwargs):
        course_id = unicode(course.id)
        home_fragment_view = SelectionPageFragmentView()
        return home_fragment_view.render_to_fragment(request, course_id=course_id, **kwargs)


class DashboardPageFragmentView(CourseHomeFragmentView):
    outline_fragment_view = DashboardPageOutlineFragmentView


class DashboardPageView(CourseTabView):
    """
    The dashboard page
    """
    def get(self, request, **kwargs):
        active_course = ActiveCourseSetting.objects.last()
        if active_course:
            course_id = unicode(active_course.course.id)
        else:
            raise Http404
        return super(DashboardPageView, self).get(request, course_id, 'courseware', **kwargs)

    def render_to_fragment(self, request, course=None, **kwargs):
        course_id = unicode(course.id)
        home_fragment_view = DashboardPageFragmentView()
        return home_fragment_view.render_to_fragment(request, course_id=course_id, **kwargs)
