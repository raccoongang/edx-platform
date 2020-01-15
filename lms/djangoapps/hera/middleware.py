from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

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
            'dashboard'
        ]
        course_urls = [
            'courseware',
            'jump_to'
        ]
        active_course = ActiveCourseSetting.objects.last()
        if active_course:
            for course_url in course_urls:
                urls.append('courses{}{}'.format(active_course.course.id, course_url))
        return urls

    def is_allowed(self, current_path):
        for path in self.allowed_urls:
            if current_path.replace('/', '').startswith(path) or current_path == "/":
                return True
        return False

    def process_request(self, request):
        is_path_allowed = self.is_allowed(request.path)
        is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == 'XMLHttpRequest'
        if request.user.is_authenticated() and not request.user.is_staff and not is_ajax and not is_path_allowed:
            if not ActiveCourseSetting.objects.all().exists():
                raise Http404
            raise Http404
        if not request.path == reverse('hera:onboarding') and request.user.is_authenticated():
            user_onboarding = UserOnboarding.objects.filter(user=request.user).first()
            if not user_onboarding or not user_onboarding.is_passed():
                return HttpResponseRedirect(reverse('hera:onboarding'))
