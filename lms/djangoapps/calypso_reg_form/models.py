from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class ExtraInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=255,
    )

    address = models.CharField(
        verbose_name=_('Address'),
        max_length=255,
    )

    zip_code = models.CharField(
        verbose_name=_('Zip'),
        max_length=255,
    )

    usa_state = models.CharField(
        verbose_name=_('State'),
        max_length=255,
    )

    def __unicode__(self):
        return unicode(self.user)


class StateExtraInfo(models.Model):
    extra_info = models.ForeignKey('ExtraInfo')
    state = models.CharField(
        verbose_name=_('State'),
        max_length=2,
        choices=settings.US_STATE_CHOICES,
    )
    license = models.CharField(
        verbose_name=_('License'),
        max_length=255,
    )

    class Meta:
        unique_together = ('extra_info', 'state',)
