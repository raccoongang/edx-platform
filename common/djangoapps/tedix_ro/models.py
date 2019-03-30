from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from student.models import AUDIT_LOG
from student.views.management import compose_and_send_activation_email

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

phone_validator = RegexValidator(regex=r'^\d{10,15}$', message='Phone length should be from 10 to 15')


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
    user = models.OneToOneField(User, related_name='%(class)s', on_delete=models.CASCADE)
    phone = models.CharField(_('phone'), validators=[phone_validator], max_length=15)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.user)


class InstructorProfile(UserProfile):
    """
    Related model for instructor profile
    """


class StudentProfile(UserProfile):
    """
    Related model for student profile
    """
    instructor = models.ForeignKey(InstructorProfile, related_name='students', null=True, on_delete=models.SET_NULL)
    classroom = models.CharField(_('classroom'), choices=CLASSROOM_CHOICES, max_length=254)
    school_city = models.ForeignKey(City)
    school = models.ForeignKey(School)
    paid = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user)

    def save(self, *args, **kwargs):
        super(StudentProfile, self).save(*args, **kwargs)

        # If this attribute is here, other needed fields are passed as well
        # These attrs are passed from tedix_ro.forms.StudentRegisterForm manually
        if getattr(self, 'parent_user', None):
            parent_profile, created = ParentProfile.objects.get_or_create(
                user=self.parent_user,
                phone=self.parent_phone
            )
            parent_profile.students.add(self)
            if created:
                # Send activation email to the parent as well
                compose_and_send_activation_email(self.parent_user, self.profile, self.registration)


class ParentProfile(UserProfile):
    """
    Related model for parent profile
    """
    students = models.ManyToManyField(StudentProfile, related_name='parents')

    def __unicode__(self):
        return unicode(self.user)


@receiver(user_logged_in)
def student_parent_logged_in(sender, request, user, **kwargs):  # pylint: disable=unused-argument
    """
    Relogin as student when parent logins successfully
    """
    try:
        parent_profile = user.parentprofile
        AUDIT_LOG.info(u'Parent Login success - {0} ({1})'.format(user.username, user.email))
        student = parent_profile.students.first() if parent_profile else None
        if student is not None and student.user.is_active:
            login(request, student.user, backend=settings.AUTHENTICATION_BACKENDS[0])
            AUDIT_LOG.info(u'Relogin as parent student - {0} ({1})'.format(student.user.username, student.user.email))
    except ParentProfile.DoesNotExist:
        pass
