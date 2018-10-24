from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from edxmako.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.contrib.sites.models import Site


@login_required
@csrf_exempt
def update_wallet(request):
    if request.method == 'POST' and request.is_ajax():
        data = request.POST.copy()
        if data.get('wallet_name'):
            resp = requests.post('http://195.160.222.156/api/wallet/update', data={
                'student_id': request.user.email,
                'lms_url': Site.objects.get_current().domain,
                'wallet': data.get('wallet_name')
            })
            return HttpResponse(resp.content, content_type="application/json")
        return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)


@login_required
@csrf_exempt
def generate_wallet(request):
    if request.method == 'POST' and request.is_ajax():
        resp = requests.post('http://195.160.222.156/api/wallet/store', data={
            'student_id': request.user.email,
            'lms_url': Site.objects.get_current().domain,
        })
        return HttpResponse(resp.content, content_type="application/json")
    else:
        return HttpResponse(status=405)
