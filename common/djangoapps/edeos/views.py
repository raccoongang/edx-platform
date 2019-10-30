"""
Edeos views.

e.g. wallets management.
"""

import httplib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from edeos.utils import (
    get_user_id,
    send_edeos_api_request,
    validate_wallets_data,
)
from student.models import UserProfile


@login_required
@csrf_exempt
def update_wallet(request):
    if request.method == 'POST' and request.is_ajax():
        data = request.POST.copy()
        profitonomy_public_key = data.get('profitonomy_public_key')
        wallet_name = data.get('wallet_name')
        if wallet_name and profitonomy_public_key:
            if not validate_wallets_data(wallet_name, profitonomy_public_key):
                return HttpResponse(status=httplib.BAD_REQUEST)
            edeos_post_data = {
                'payload': {
                    'student_id': get_user_id(request.user),
                    'client_id': getattr(settings, 'EDEOS_API_KEY'),
                    'wallet': wallet_name,
                    'public_key': profitonomy_public_key,
                },
                "api_endpoint": "wallet_store",
                "key": getattr(settings, 'EDEOS_API_KEY'),
                "secret": getattr(settings, 'EDEOS_API_SECRET'),
                "base_url": getattr(settings, 'EDEOS_API_URL')
            }
            response = send_edeos_api_request(**edeos_post_data)
            if response:
                profile = UserProfile.objects.get(user=request.user)
                if profile:
                    profile.save_profitonomy_public_key(profitonomy_public_key)
                    profile.save_wallet_name(wallet_name)
            else:
                # NOTE: handle the code from edeos api (major refactoring needed)
                return HttpResponse(status=httplib.BAD_REQUEST)
            return HttpResponse(response, status=httplib.OK, content_type="application/json")
        return HttpResponse(status=httplib.BAD_REQUEST)
    else:
        return HttpResponse(status=httplib.METHOD_NOT_ALLOWED)


@login_required
@csrf_exempt
def generate_wallet(request):
    if request.method == 'POST' and request.is_ajax():
        edeos_post_data = {
            'payload': {
                'student_id': get_user_id(request.user),
                'client_id': getattr(settings, 'EDEOS_API_KEY'),
            },
            "api_endpoint": "wallet_store",
            "key": getattr(settings, 'EDEOS_API_KEY'),
            "secret": getattr(settings, 'EDEOS_API_SECRET'),
            "base_url": getattr(settings, 'EDEOS_API_URL')
        }
        response = send_edeos_api_request(**edeos_post_data)
        return HttpResponse(response, content_type="application/json")
    else:
        return HttpResponse(status=httplib.METHOD_NOT_ALLOWED)
