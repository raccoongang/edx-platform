from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

class webform(models.Model):

    courseid = models.CharField(
        verbose_name="Courseid",
        max_length=100,null=False
    )

    sheeturl = models.CharField(
        verbose_name="Url",
        max_length=300,null=False
    ) 

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    location = models.CharField(
        verbose_name="Location",
        max_length=200,null=False
    )

    question = models.CharField(
        verbose_name="Question",
        max_length=200,null=False
    )

    feedback_form_link = models.CharField(
        verbose_name="Feedback Form Link",
        max_length=500,null=False
    )

    class Meta:
        """ Meta class for this Django model """
        verbose_name = _('Google Forms')
        verbose_name_plural = _('Google Forms')

    def __unicode__(self):
        return self.courseid
