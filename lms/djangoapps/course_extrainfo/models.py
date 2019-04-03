from django.db import models
from django.utils.translation import ugettext_lazy as _
from lms.djangoapps.specialization.models import specializations, categories
# Create your models here.

class course_extrainfo(models.Model):

	course_id = models.CharField(max_length=255, db_index=True)

	course_type = models.CharField(
		verbose_name="Course_type",
		max_length=2,
	)
	specialization = models.ForeignKey(specializations, null=True)
	category = models.CharField(max_length=2, db_index=True, null=True)
	sub_category = models.CharField(max_length=150, db_index=True, null=True)

	def __unicode__(self):
		return self.course_id

