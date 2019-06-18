from django import forms
from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from .models import CourseCategory


class CourseMultipleModelChoiceField(forms.ModelMultipleChoiceField):

    def clean(self, value):
        value = map(CourseKey.from_string, value)
        return super(CourseMultipleModelChoiceField, self).clean(value)


class CourseCategoryForm(forms.ModelForm):
    courses = CourseMultipleModelChoiceField(queryset=CourseOverview.objects.all(), required=False)


class CourseCategoryAdmin(DjangoMpttAdmin):
    form = CourseCategoryForm
    tree_auto_open = True
    prepopulated_fields = {'slug': ('name',)}
    # for DjangoMpttAdmin fields = '__all__' doesn't work
    fields = ['name', 'slug', 'description', 'courses']

admin.site.register(CourseCategory, CourseCategoryAdmin)
