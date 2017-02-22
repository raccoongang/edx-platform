from django.conf import settings
from django.contrib.auth.decorators import login_required

from edxmako.shortcuts import render_to_response


@login_required
def dashboard(request):
    if (
        settings.FEATURES.get('ENABLE_GAMMA', False) and
        settings.FEATURES.get('GAMMA_PROPERTIES', {}) and
        settings.FEATURES.get('GAMMA_PROPERTIES', {}).get('PUBLIC_URL')
    ):
        public_url = settings.FEATURES.get('GAMMA_PROPERTIES', {}).get('PUBLIC_URL')

    context = {
        'public_url': public_url,
    }

    return render_to_response('gamification.html', context)

