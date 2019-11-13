from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from certificates.models import GeneratedCertificate
from courseware.models import UserCheckActivityConfig
from student.models import CourseEnrollment


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


class UserSpendTimeCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    course_id = CourseKeyField(max_length=255, db_index=True)
    spend_time = models.IntegerField(default=0)
    check_activity = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course_id',)

    def __unicode__(self):
        return (
            "user - {}, course_id - {}, spend_time - {} seconds"
        ).format(self.user, self.course_id, self.spend_time)

    @property
    def is_track(self):
        course_enrollment = CourseEnrollment.get_enrollment(self.user, self.course_id)
        user_check_activity_config = UserCheckActivityConfig.current()
        return (
                user_check_activity_config.enabled
                and course_enrollment
                and course_enrollment.created >= user_check_activity_config.start_tracking
                and not GeneratedCertificate.certificate_for_student(self.user, self.course_id)
        )
