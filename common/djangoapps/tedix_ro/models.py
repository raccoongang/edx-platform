from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

phone_validator = RegexValidator(regex=r'^\d{10,15}$', message='Phone length should to be from 10 to 15')


class StudentParent(models.Model):
    """
    Related model for student and his parents
    """
    user = models.OneToOneField(User, related_name='parent_profile', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='parents')
    phone = models.CharField(_('phone'), validators=[phone_validator], max_length=15)

    def __unicode__(self):
        return unicode(self.user)
