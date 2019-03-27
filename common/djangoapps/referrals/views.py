from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from models import Referral
from utils import hashkey_generator


def user_referral(request, hashkey):
    referral = get_object_or_404(Referral, hashkey=hashkey)
    response = HttpResponseRedirect(reverse('dashboard'))
    if hasattr(request.user, "email"):
        if request.user.email != referral.user.email:
            response.set_cookie('referral_id', referral.id)
    else:
        response.set_cookie('referral_id', referral.id)
    return response


class GetHashKeyView(APIView):
    """
    Get referral hash key for a current user.

    Current user is a referer.
    """

    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(csrf_exempt)
    def post(self, request):
        """
        Handler for the POST method to this view.
        """
        referral, created = Referral.objects.get_or_create(user=request.user)
        if referral:
            return Response({'hashkey': reverse('referrals:user_referral', kwargs={'hashkey': referral.hashkey})})
        else:
            return Response({'hashkey': ""})
