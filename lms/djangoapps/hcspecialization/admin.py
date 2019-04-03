from django.contrib import admin
from .models import hcspecializations

class HcspecializationAdmin(admin.ModelAdmin):
    
    list_display = [
        'name'
    ] 

    search_fields = ['name']

admin.site.register(hcspecializations)