from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from student.models import AUDIT_LOG

CLASSROOM_CHOICES = (
    ('', ''),

    ('7A', '7A'),
    ('7B', '7B'),
    ('7C', '7C'),
    ('7D', '7D'),

    ('8A', '8A'),
    ('8B', '8B'),
    ('8C', '8C'),
    ('8D', '8D'),
)

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


class UserProfile(models.Model):
    user = None  # Need to implement
    city = models.ForeignKey(City)
    school = models.ForeignKey(School)
    phone = models.CharField(_('phone'), validators=[phone_validator], max_length=15)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.user)


class InstructorProfile(UserProfile):
    """
    Related model for instructor profile
    """
    user = models.OneToOneField(User, related_name='instructor_profile', on_delete=models.CASCADE)


class StudentProfile(UserProfile):
    """
    Related model for student profile
    """
    user = models.OneToOneField(User, related_name='student_profile', on_delete=models.CASCADE)
    instructor = models.ForeignKey(InstructorProfile, related_name='students', null=True, on_delete=models.SET_NULL)
    classroom = models.CharField(_('classroom'), choices=CLASSROOM_CHOICES, max_length=254)

    def __unicode__(self):
        return unicode(self.user)


class ParentProfile(UserProfile):
    """
    Related model for student and his parents
    """
    user = models.OneToOneField(User, related_name='parent_profile', on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentProfile, related_name='parents')

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
    except ParentProfile.DoesNotExist:
        pass
