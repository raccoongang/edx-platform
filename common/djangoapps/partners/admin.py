"""
Admin site bindings for the `partners` app.
"""

from django.contrib import admin

from partners.models import Partner


class PartnerAdmin(admin.ModelAdmin):
    """
    Admin interface for the `Partner` model.
    """

    model = Partner
    readonly_fields = ('created', 'modified')
    list_display = ('name', 'url')
    search_fields = ['name']


admin.site.register(Partner, PartnerAdmin)
