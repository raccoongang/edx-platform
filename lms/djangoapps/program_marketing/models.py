from django.db import models


class ProgramMarketing(models.Model):
    """
    Contains program marketing attributes.
    """
    marketing_slug = models.SlugField(max_length=64)
    title = models.CharField(max_length=128, blank=True)
    # TODO avoid using program_id
    program_id = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField()
    promo_video_url = models.URLField(blank=True)
    promo_image_url = models.URLField(blank=True)

