from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class specializations(models.Model):

	name = models.CharField(
		verbose_name="Specialization",
		max_length=100,
	)

	def __unicode__(self):
		return self.name

class sub_categories(models.Model):
    sub_topic_name = models.CharField(max_length=50)

    def __unicode__(self):
            return self.sub_topic_name

class categories(models.Model):
    topic_name = models.CharField(max_length=50)
    topic_short_name = models.CharField(max_length=50, null=True)
    topic_image = models.CharField(max_length=255, null=True)
    sub_category = models.ManyToManyField(sub_categories, db_index=True, related_name='sub_category')
    topic_specialization = models.ManyToManyField(specializations, db_index=True, related_name='cat_specialization')

    def __unicode__(self):
            return self.topic_name
            
class cat_sub_category(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(categories)

    def __unicode__(self):
            return self.name