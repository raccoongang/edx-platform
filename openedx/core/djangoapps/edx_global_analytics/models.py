"""
Models for the edX global analytics application.
"""

from django.db import models


class AccessTokensStorage(models.Model):
    """
    This model represents relationship`s key with analytics-server.

    `access_token` is a sequence of characters as special key for data sending access.
    """
    access_token = models.CharField(max_length=255, null=True)
