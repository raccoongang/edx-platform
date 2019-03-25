from django.db import models
from django.contrib.auth.models import User
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from utils import hashkey_generator


class Referral(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUSES = [
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_INACTIVE, STATUS_INACTIVE)
    ]
    STUDENT_SIGNUP = "student_signup"
    COURSE_ENROLLMENT = "course_enrollment"
    TYPES = [
        (STUDENT_SIGNUP, COURSE_ENROLLMENT)
    ]

    user = models.ForeignKey(User, db_index=True)  # Referer
    course_id = CourseKeyField(max_length=255, db_index=True, null=True)
    client_id = models.CharField(max_length=10)  # Edeos issued client id (unique identifier of an LMS site)
    type = models.CharField(max_length=10, default=STUDENT_SIGNUP)
    hashkey = models.CharField(max_length=32, unique=True, default=hashkey_generator)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_ACTIVE)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)


class ActivatedLink(models.Model):
    referral = models.ForeignKey(Referral)
    user = models.ForeignKey(User)
    used = models.BooleanField(default=False)
