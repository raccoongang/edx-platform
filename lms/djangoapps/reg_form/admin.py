from django.contrib import admin
from .models import extrafields
from lms.djangoapps.specialization.models import specializations

class ExtrafieldsAdmin(admin.ModelAdmin):
    
    list_display = [
        'phone','user','reg_num','specializations','user_type','pincode',
    ]
    search_fields = ['user','user_type']

admin.site.register(extrafields)