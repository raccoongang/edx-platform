from django.db import models
from django.contrib.auth.models import User
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from utils import hashkey_generator


class Referrals(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUSES = [
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_INACTIVE, STATUS_INACTIVE)
    ]
    user = models.ForeignKey(User, db_index=True)
    course_id = CourseKeyField(max_length=255, db_index=True)
    hashkey = models.CharField(max_length=32, unique=True, default=hashkey_generator)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_ACTIVE)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)


class ActivatedLinks(models.Model):
    referral = models.ForeignKey(Referrals)
    user = models.ForeignKey(User)
    used = models.BooleanField(default=False)
