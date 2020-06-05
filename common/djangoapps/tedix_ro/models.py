from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from opaque_keys.edx.django.models import CourseKeyField

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import AUDIT_LOG
from student.views.management import compose_and_send_activation_email


phone_validator = RegexValidator(regex=r'^\d{10,15}$', message=_('The phone number length must be from 10 to 15 digits.'))


class Classroom(models.Model):
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u'{}'.format(self.name)


class City(models.Model):
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return self.name


class School(models.Model):
    TYPE_CHOICES = [
        ('Public', 'Public'),
        ('Private', 'Private')
    ]
    name = models.CharField(max_length=254)
    city = models.ForeignKey(City, related_name='schools', null=True, on_delete=models.CASCADE)
    school_type = models.CharField(max_length=55, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'city']

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='%(class)s', on_delete=models.CASCADE)
    phone = models.CharField(_('phone'), validators=[phone_validator], max_length=15)

    class Meta:
        abstract = True

    def __unicode__(self):
        try:
            return u'{}'.format(self.user.profile.name or self.user.username)
        except ObjectDoesNotExist:
            return u'{}'.format(self.user.username)


class InstructorProfile(UserProfile):
    school_city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    """
    Related model for instructor profile
    """


class StudentProfile(UserProfile):
    """
    Related model for student profile
    """
    instructor = models.ForeignKey(InstructorProfile, related_name='students', null=True, on_delete=models.SET_NULL, blank=True)
    school_city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    paid = models.BooleanField(default=False)
    classroom = models.ForeignKey(Classroom, related_name='students', null=True, on_delete=models.SET_NULL)

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


class ParentProfile(UserProfile):
    """
    Related model for parent profile
    """
    students = models.ManyToManyField(StudentProfile, related_name='parents')

    def __unicode__(self):
        return unicode(self.user)


class StudentCourseDueDate(models.Model):
    due_date = models.DateTimeField()
    student = models.ForeignKey(StudentProfile, related_name='course_due_dates', on_delete=models.CASCADE)
    course_id = CourseKeyField(max_length=255, db_index=True)

    class Meta:
        unique_together = ('student', 'course_id')

    def __unicode__(self):
        return _(u'Student course due date')


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


class VideoLesson(models.Model):
    user = models.ForeignKey(User, related_name='video_lessons', on_delete=models.CASCADE)
    course = CourseKeyField(max_length=255)
    video_id = models.CharField(max_length=255)


class Question(models.Model):
    video_lesson = models.ForeignKey(VideoLesson, related_name='questions', on_delete=models.CASCADE)
    question_id = models.CharField(max_length=255)
    attempt_count = models.IntegerField()


class StudentReportSending(models.Model):
    course_id = CourseKeyField(max_length=255)
    user = models.ForeignKey(User, related_name='stident_report_sending', on_delete=models.CASCADE)
    grade = models.FloatField()
