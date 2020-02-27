from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from student.models import CourseEnrollment, CourseEnrollmentAllowed

from .models import ActiveCourseSetting, UserOnboarding


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
        ]
        course_urls = [
            'courseware',
            'jump_to'
        ]
        active_course_id = ActiveCourseSetting.get()
        if active_course_id:
            for course_url in course_urls:
                urls.append('courses{}{}'.format(active_course_id, course_url))
        return urls

    def is_allowed(self, current_path):
        for path in self.allowed_urls:
            if current_path.replace('/', '').startswith(path) or current_path == "/":
                return True
        return False

    def process_request(self, request):
        user = request.user
        if user.is_authenticated():
            is_path_allowed = self.is_allowed(request.path)
            is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == 'XMLHttpRequest'
            if not user.is_staff:
                if not is_ajax and not is_path_allowed:
                    raise Http404
                # lets logged in users to activate their accounts
                if '/activate/' in request.path:
                    return
                if 'logout' in request.path:
                    return # let students logout
                if not user.is_active:
                    if CourseEnrollmentAllowed.for_user(user).filter(auto_enroll=True):
                        if not request.path == reverse('hera:register_success'):
                            return HttpResponseRedirect(reverse('hera:register_success'))
                        else:
                            return
                active_course_id = ActiveCourseSetting.get()
                if active_course_id:
                    if not CourseEnrollment.is_enrolled(user, active_course_id):
                        raise Http404
                else:
                    raise Http404
                if not request.path == reverse('hera:onboarding'):
                    if not UserOnboarding.onboarding_is_passed(request.user.id):
                        return HttpResponseRedirect(reverse('hera:onboarding'))
