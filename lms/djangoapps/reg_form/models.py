from django.conf import settings
from django.db import models
from lms.djangoapps.specialization.models import specializations
from lms.djangoapps.hcspecialization.models import hcspecializations

from django.utils.translation import ugettext_noop
# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class extrafields(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=True, related_name='extrafields')

    phone = models.CharField(blank=True, max_length=255, db_index=True)

    rcountry = models.CharField(blank=True, max_length=255, db_index=True)
    rstate = models.CharField(blank=True, max_length=255, db_index=True)
    rcity = models.CharField(blank=True, max_length=255, db_index=True)
    address = models.CharField(blank=True, max_length=255, db_index=True)

    rpincode = models.CharField(blank=True, max_length=6, db_index=True)

    specialization = models.ForeignKey(specializations, null=True)

    hcspecialization = models.ForeignKey(hcspecializations, null=True)


    reg_num = models.CharField(
        verbose_name="Reg Num",
        max_length=100,
    )

    USER_TYPE = (
        ('dr', ugettext_noop('Doctor')),
        ('u', ugettext_noop('User')),
        # Translators: 'Other' refers to the student's gender
        ('ms', ugettext_noop('Medical Student')),
        ('hc', ugettext_noop('Health Care Proffessional'))
    )
    user_type = models.CharField(
        default='dr', null=False, max_length=2, db_index=True, choices=USER_TYPE
    )

    @property
    def usertype_display(self):
        """ Convenience method that returns the human readable user_type. """
        if self.user_type:
            return self.__enumerable_to_display(self.USER_TYPE, self.user_type)

    def __unicode__(self):
        return u"{}".format(self.user)
