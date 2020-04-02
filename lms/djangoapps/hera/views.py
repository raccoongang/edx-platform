"""
View which retrieve hera onboarding pages and handle user onboarding states.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.utils.decorators import method_decorator

from edxmako.shortcuts import render_to_response
from hera.fragments import DashboardPageOutlineFragmentView, SelectionPageOutlineFragmentView
from hera.models import ActiveCourseSetting, Mascot, UserOnboarding
from hera.utils import get_user_active_course_id
from lms.djangoapps.courseware.views.views import CourseTabView
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
        if request.user and user_onboarding.is_passed():
            course_id = get_user_active_course_id(request.user)
            kwargs={}
            if course_id:
                kwargs={'course_id': get_user_active_course_id(request.user)}
            return HttpResponseRedirect(reverse(
                'hera:dashboard',
                kwargs=kwargs
            ))
        context = {
            'pages': user_onboarding.get_pages(),
            'current_page': user_onboarding.get_current_page(),
            'is_passed': user_onboarding.is_passed(),
            'onboarding_mascot': Mascot.onboarding_img_url()
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
        home_fragment_view = SelectionPageFragmentView()
        return home_fragment_view.render_to_fragment(request, course_id=unicode(course.id), **kwargs)


class DashboardPageFragmentView(CourseHomeFragmentView):
    outline_fragment_view = DashboardPageOutlineFragmentView


@method_decorator(login_required, name='dispatch')
class DashboardPageView(CourseTabView):
    """
    The dashboard page
    """
    def get(self, request, course_id=None, **kwargs):
        active_course_id = course_id or get_user_active_course_id(request.user)
        if not active_course_id:
            return render_to_response("hera/not-found/not-found-ask.html")
        return super(DashboardPageView, self).get(request, unicode(active_course_id), 'courseware', **kwargs)

    def render_to_fragment(self, request, course=None, **kwargs):
        home_fragment_view = DashboardPageFragmentView()
        return home_fragment_view.render_to_fragment(request, course_id=unicode(course.id), **kwargs)


class RegisterSuccessView(View):

    def get(self, equest, **kwargs):
        return render_to_response("hera/register_success.html")
