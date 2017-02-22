from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404

from opaque_keys.edx.keys import CourseKey
from models import Referrals, ActivatedLinks
from utils import hashkey_generator


def user_referral(request, hashkey):
    referral = get_object_or_404(Referrals, hashkey=hashkey, status=Referrals.STATUS_ACTIVE)
    if not request.user.is_authenticated():
        request.session['referral'] = {
            'course_id': unicode(referral.course_id),
            'user_id': referral.user.pk,
            'referral_id': referral.id
        }
    else:
        ActivatedLinks.objects.get_or_create(
            referral=referral,
            user=request.user
        )
    course_redirect = reverse('course_root', kwargs={'course_id': unicode(referral.course_id)})
    return redirect(course_redirect)


class GetHashKeyView(APIView):
    """
    API response which return referral's hash key for current user and course
    """

    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(csrf_exempt)
    def post(self, request):
        """
        Handler for the POST method to this view.
        """

        referral, created = Referrals.objects.get_or_create(
            user=request.user,
            course_id=CourseKey.from_string(request.data.get('course_id')),
        )
        if not created:
            referral.hashkey = hashkey_generator()
            referral.status = Referrals.STATUS_ACTIVE
            referral.save()
        return Response({'hashkey': reverse('referrals:user_referral', kwargs={'hashkey': referral.hashkey})})
