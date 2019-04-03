from django.contrib import admin
from .models import case_study_abstracts
# Register your models here.

@admin.register(case_study_abstracts)
class Case_study_abstractsAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'title')
    search_fields = ('user_id', 'title')
