"""
Admin interface for LTI Provider app.
"""

from django.contrib import admin

from .models import ProgramMarketing



class ProgramMarketingAdmin(admin.ModelAdmin):
    """Admin for ProgramMarketing"""
    list_display = ('marketing_slug', 'description', 'promo_video_url')


admin.site.register(ProgramMarketing, ProgramMarketingAdmin)
