from django.contrib import admin
from .models import contactform

class SpecializationAdmin(admin.ModelAdmin):
    
    list_display = [
        'name','emailid','created_at'
    ]

    search_fields = ['name','emailid','created_at']

admin.site.register(contactform)