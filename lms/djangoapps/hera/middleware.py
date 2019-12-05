from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import UserOnboarding

class OnboardingMiddleware(object):
    """
    Redirect users to the Onboarding Page if they haven't passed it yet.
    """
    ALLOWED_URLS = [
        'onboarding',
        'logout',
        'admin',
    ]

    def is_allowed(self, current_path):
        for path in self.ALLOWED_URLS:
            if current_path.replace('/', '').startswith(path):
                return True
        return False

    def process_request(self, request):
        is_path_allowed = self.is_allowed(request.path)
        is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == 'XMLHttpRequest'
        if request.user.is_authenticated() and not request.user.is_staff and not is_ajax and not is_path_allowed:
            user_onboarding = UserOnboarding.objects.filter(user=request.user).first()
            if not user_onboarding or not user_onboarding.is_passed():
                return HttpResponseRedirect(reverse('hera:onboarding'))
