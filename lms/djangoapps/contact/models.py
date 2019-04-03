from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class contactform(models.Model):

	name = models.CharField(
		verbose_name="name",
		max_length=100,
	)

	emailid = models.CharField(blank=False, max_length=255, db_index=True)

	message = models.CharField(blank=True, null=True, max_length=3000, db_index=False,)

	inquiry_type = models.CharField(null=False, max_length=2, db_index=True,)

	phone = models.CharField(blank=False, max_length=13, db_index=True,)
	
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name
