from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class hcspecializations(models.Model):

	name = models.CharField(
		verbose_name="Hcspecialization",
		max_length=100,
	)

	def __unicode__(self):
		return self.name
 