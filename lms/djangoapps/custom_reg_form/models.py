from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class ExtraInfo(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    STUDENT = 'ST'
    INSTRUCTOR = 'IN'
    USER_ROLES_CHOICES = (
        (STUDENT, _('Student')),
        (INSTRUCTOR, _('Instructor')),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    street = models.CharField(
        verbose_name=_('Street'),
        max_length=255,
    )

    street_number = models.CharField(
        verbose_name=_('Street Number'),
        max_length=50,
    )

    place = models.CharField(
        verbose_name=_('Place'),
        max_length=255,
    )

    zip_code = models.CharField(
        verbose_name=_('Zip Code'),
        max_length=50,
    )

    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=20,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        verbose_name=_('Date of Birth'),
        blank=True,
        null=True
    )

    user_role = models.CharField(
        verbose_name=_('User Role'),
        max_length=2,
        choices=USER_ROLES_CHOICES,
        default=STUDENT,
    )
