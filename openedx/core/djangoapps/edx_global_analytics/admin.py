"""
Django admin page for edX global analytics application.
"""

from django.contrib import admin

from openedx.core.djangoapps.edx_global_analytics.models import AccessTokensStorage


class AccessTokensStorageAdmin(admin.ModelAdmin):
    """
    Admin for access tokens storage.
    """
    fields = ['access_token']

admin.site.register(AccessTokensStorage, AccessTokensStorageAdmin)
