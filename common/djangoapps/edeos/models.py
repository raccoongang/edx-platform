from django.db import models
from django.utils.translation import ugettext_noop

from student.models import UserProfile


class UserSocialLink(models.Model):
    """
    Represents a user's social platforms links.
    """
    # LINKEDIN = 'linkedin'
    FACEBOOK = 'facebook'

    PLATFORM_CHOICES = (
        # (LINKEDIN, ugettext_noop('LinkedIn')),
        (FACEBOOK, ugettext_noop('Facebook')),
    )

    VALID_URLS = {
        FACEBOOK: 'Facebook.com/'
    }

    user_profile = models.ForeignKey(UserProfile, db_index=True, related_name='social_links', on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    social_link = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)

    class Meta(object):
        unique_together = (('user_profile', 'platform',),)
        ordering = ('user_profile',)

    def __str__(self):
        return "%s | %s" % (self.user_profile.user.email, self.platform)
