from django.contrib import admin

from dashboard.models import EmailsAdressMailing

@admin.register(EmailsAdressMailing)
class EmailsAdressMailingAdmin(admin.ModelAdmin):
    fields = ('email', 'comment', 'active')
    list_display = ('email', 'comment', 'active')
    list_filter = ('active',)
    search_fields = ['email']
