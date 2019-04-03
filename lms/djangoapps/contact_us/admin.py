from django.contrib import admin
from .models import contact_us_form

class Contact_Us_Form_Admin(admin.ModelAdmin):
    
    list_display = [
        'name','emailid','created_at'
    ]

    search_fields = ['name','emailid','created_at']

admin.site.register(contact_us_form)