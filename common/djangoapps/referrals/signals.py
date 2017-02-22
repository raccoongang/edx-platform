from django.contrib.auth.signals import user_logged_in

from .models import ActivatedLinks, Referrals


def add_referral(sender, user, request, **kwargs):
    referral_info = request.session.get('referral')
    if referral_info and referral_info.get('referral_id'):
        referral = Referrals.objects.filter(id=referral_info['referral_id']).first()
        ActivatedLinks.objects.get_or_create(
            referral=referral,
            user=request.user
        )


user_logged_in.connect(add_referral)
