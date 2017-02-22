from django.contrib.auth.signals import user_logged_in

from .models import ActivatedLinks, Referrals


def add_referral(sender, user, request, **kwargs):
    referral_info = request.session['referral']
    if referral_info and referral_info.get('referral_id'):
        referral = Referrals.objects.filter(id=referral_info['referral_id'])
        ActivatedLinks.objects.get_or_create(
            referral=referral,
            user=request.user
        )


user_logged_in.connect(add_referral)
