from django.contrib import admin
from .models import course_extrainfo

class Course_extrainfo_Admin(admin.ModelAdmin):
    
    list_display = [
        'course_id','course_type','specialization'
    ]

    search_fields = ['course_id','specialization']

admin.site.register(course_extrainfo)
