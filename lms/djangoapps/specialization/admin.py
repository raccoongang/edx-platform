from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from lms.djangoapps.specialization.models import (specializations, categories, sub_categories, cat_sub_category)

@admin.register(specializations)
class SpecializationAdmin(admin.ModelAdmin):

    list_display = ('name',)
    search_fields = ('name',)

@admin.register(categories)
class CategoriesAdmin(admin.ModelAdmin):

    list_display = ('topic_name', 'topic_short_name', 'topic_image',)
    search_fields = ('topic_name',)

@admin.register(sub_categories)
class SubCategoriesAdmin(admin.ModelAdmin):

    list_display = ('sub_topic_name',)
    search_fields = ('sub_topic_name',)

@admin.register(cat_sub_category)
class CatSubCategoriesAdmin(admin.ModelAdmin):

    list_display = ('name',)
    search_fields = ('category',)
