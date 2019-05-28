from django import forms
from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from models import CourseCategory


class CourseMultipleModelChoiceField(forms.ModelMultipleChoiceField):

    def clean(self, value):
        value = map(CourseKey.from_string, value)
        return super(CourseMultipleModelChoiceField, self).clean(value)


class CourseCategoryForm(forms.ModelForm):
    courses = CourseMultipleModelChoiceField(queryset=CourseOverview.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(CourseCategoryForm, self).__init__(*args, **kwargs)

    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if self.instance.id and parent in self.instance.get_descendants(include_self=True):
            self.add_error('parent',
                'A category or subcategory can\'t be a parent of itself. '
                'A subcategory can\'t be a parent of its parent category.'
            )
        return parent


class CourseCategoryAdmin(DjangoMpttAdmin):

    form = CourseCategoryForm
    tree_auto_open = True
    prepopulated_fields = {'slug': ('name',)}
    # for DjangoMpttAdmin fields = '__all__' doesn't work
    fields = ['name', 'slug', 'img', 'description', 'parent', 'url', 'courses']


admin.site.register(CourseCategory, CourseCategoryAdmin)
