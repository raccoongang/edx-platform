from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import UserOnboarding

class OnboardingMiddleware(object):
    """
    Redirect users to the Onboarding Page if they haven't passed it yet.
    """

    def process_request(self, request):
        allowed_urls = [reverse('hera:onboarding'), reverse('logout')]
        is_path_allowed = request.path in allowed_urls
        is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == 'XMLHttpRequest'
        if request.user.is_authenticated() and not is_ajax and not is_path_allowed:
            user_onboarding = UserOnboarding.objects.filter(user=request.user).first()
            if not user_onboarding or not user_onboarding.is_passed():
                return HttpResponseRedirect(reverse('hera:onboarding'))
