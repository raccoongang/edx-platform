from django.db import models
from django.contrib.auth.models import User

from utils import hashkey_generator


class Referral(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUSES = [
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_INACTIVE, STATUS_INACTIVE)
    ]

    user = models.ForeignKey(User, db_index=True)  # Referer
    hashkey = models.CharField(max_length=32, unique=True, default=hashkey_generator)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_ACTIVE)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)


class ActivatedLink(models.Model):
    """
    Model to store links used by users.

    For example, store referrals assignments
    to newly registered users.

    Instantiating doesn't necessarily mean
    setting referral's status to "inactive".

    Also, it doesn't mean that third-party business rules
    of referrals activation are necessarily met, e.g.
    for Edeos, a referral is considered "activated"
    only if a user activated their account, while
    we store the activation link before it happens
    (upon new account creation), to double-check a
    referral in future if none found in
    cookies or session.
    """
    referral = models.ForeignKey(Referral)
    user = models.ForeignKey(User)
    used = models.BooleanField(default=False)
