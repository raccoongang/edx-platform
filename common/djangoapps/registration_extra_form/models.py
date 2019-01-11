from django.conf import settings
from django.db import models

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

    def __unicode__(self):
        return u'{}'.format(self.user.email)
