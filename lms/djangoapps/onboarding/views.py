"""
View which retrieve onboarding pages and handle user onboarding states.
"""
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator

from edxmako.shortcuts import render_to_response

from onboarding.models import Onboarding, UserOnboarding


@method_decorator(login_required, name='dispatch')
class OnboardingPagesView(View):
    """
    Represent user onboarding pages and handle it.
    """

    def get(self, request, **kwargs):
        """
        Render user onboarding pages.
        """
        onboarding = Onboarding.objects.first()
        user_onboarding, _ = UserOnboarding.objects.select_related('onboarding').get_or_create(user=request.user, onboarding=onboarding)
        context = {
            'pages': user_onboarding.get_pages(),
            'current_page': user_onboarding.get_current_page(),
        }
        return render_to_response("onboarding/onboarding.html", context)

    def post(self, request, **kwargs):
        """
        Save user onboarding pages status.
        """
        if request.is_ajax():
            page = self.request.POST['page']
            user_onboarding = UserOnboarding.update(self.request.user, page)

            return JsonResponse({
                'success': True,
                'next_page': user_onboarding.get_next_page(page),
                'current_page': page,
            })
        return HttpResponseForbidden()
