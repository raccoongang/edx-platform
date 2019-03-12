from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator

# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class ExtraInfo(models.Model):
    user = models.OneToOneField(USER_MODEL, null=True)
    accepted_to_be_contacted = models.BooleanField(
        verbose_name='I accept to be contacted by email around Microsoft/Cloud products and Education'
    )
    interested_in = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Which Microsoft product/solution are you interested in?'
    )
    areas_to_support = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Any specific areas Arrow could support you with?'
    )
    phone_validator = RegexValidator(
        regex=r'^\d{9,15}$',
        message="The phone number must be from 9 to 15 digits inclusively."
    )
    phone = models.CharField(
        validators=[phone_validator],
        max_length=15,
        blank=True,
        verbose_name='Phone number'
    )

    def __unicode__(self):
        return u'{}'.format(self.user.email)
