from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class ExtraInfo(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    appfactory_name = models.CharField(
        blank=True,
        default='',
        max_length=160,
        verbose_name=_('AppFactory Name'),
    )
