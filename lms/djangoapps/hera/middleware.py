from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from student.models import CourseEnrollmentAllowed

from .models import UserOnboarding
from .utils import get_user_active_course_id


class AllowedUrlsMiddleware(object):
    """
    Redirect users to the Onboarding Page if they haven't passed it yet.
    Redirect users to the 404 if pages not allowed.
    """
    @property
    def allowed_urls(self):
        urls = [
            'onboarding',
            'logout',
            'admin',
            'user_dashboard',
            'event', # some system url,
            'dashboard',
            'activate',
            'register_success',
            'media',
        ]
        return urls

    def is_allowed(self, current_path, user):
        course_urls = [
            'courseware',
            'jump_to'
        ]
        active_course_id = get_user_active_course_id(user)
        allowed_urls = self.allowed_urls
        if active_course_id:
            for course_url in course_urls:
                allowed_urls.append('courses{}{}'.format(active_course_id, course_url))
        for path in allowed_urls:
            if current_path.replace('/', '').startswith(path) or current_path == "/":
                return True
        return False

    def process_request(self, request):
        user = request.user
        if user.is_authenticated():
            is_path_allowed = self.is_allowed(request.path, user)
            is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == 'XMLHttpRequest'
            if not user.is_staff:
                if not is_ajax and not is_path_allowed:
                    raise Http404
                if '/media/' in request.path:
                    return
                # lets logged in users to activate their accounts
                if '/activate/' in request.path:
                    return
                if 'logout' in request.path:
                    return # let students logout
                if not user.is_active:
                    if not request.path == reverse('hera:register_success'):
                        return HttpResponseRedirect(reverse('hera:register_success'))
                    else:
                        return
                if not request.path == reverse('hera:onboarding'):
                    if not UserOnboarding.onboarding_is_passed(request.user.id):
                        return HttpResponseRedirect(reverse('hera:onboarding'))
