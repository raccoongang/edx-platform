from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from student.models import AUDIT_LOG

phone_validator = RegexValidator(regex=r'^\d{10,15}$', message='Phone length should to be from 10 to 15')


class City(models.Model):
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class StudentParent(models.Model):
    """
    Related model for student and his parents
    """
    user = models.OneToOneField(User, related_name='parent_profile', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='parents')
    phone = models.CharField(_('phone'), validators=[phone_validator], max_length=15)

    def __unicode__(self):
        return unicode(self.user)


@receiver(user_logged_in)
def student_parent_logged_in(sender, request, user, **kwargs):  # pylint: disable=unused-argument
    """
    Relogin as student when parent logins successfully
    """
    try:
        parent_profile = user.parent_profile
        AUDIT_LOG.info(u'Parent Login success - {0} ({1})'.format(user.username, user.email))
        student = parent_profile.students.first()
        if student is not None and student.is_active:
            login(request, student, backend=settings.AUTHENTICATION_BACKENDS[0])
            AUDIT_LOG.info(u'Relogin as parent student - {0} ({1})'.format(student.username, student.email))
    except StudentParent.DoesNotExist:
        pass
