from django.conf import settings
from django.db import models
from organizations.models import SponsoringCompany
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

# Create your models here.

class Sponsored_course_users(models.Model):
	course_id = models.CharField(max_length=255, db_index=True)
	sponsoringcompany = models.CharField(max_length=20, db_index=True, null=True)
	image_url = models.CharField(max_length=250, blank=True)
	video_url = models.CharField(max_length=250, blank=True)
	coupon_code = models.TextField(null=False)
	question = models.CharField(max_length=250, blank=True)
	answer = models.CharField(max_length=250, blank=True)

	def __unicode__(self):
		return self.course_id

class user_view_counter(models.Model):
	course_id = models.CharField(max_length=255, db_index=True)
	counter = models.CharField(max_length=255, db_index=True)
	user = models.OneToOneField(USER_MODEL, null=True)

	def __unicode__(self):
		return self.course_id