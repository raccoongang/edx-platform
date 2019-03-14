from django.contrib import admin

from dashboard.models import EmailsAddressMailing

@admin.register(EmailsAddressMailing)
class EmailsAddressMailingAdmin(admin.ModelAdmin):
    fields = ('email', 'comment', 'active')
    list_display = ('email', 'comment', 'active')
    list_filter = ('active',)
    search_fields = ['email']
