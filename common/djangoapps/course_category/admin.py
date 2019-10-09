from django import forms
from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from models import CourseCategory, Program


class ProductModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    '''
    Redefinition of clean method.

    Values that original method recieves by m2m from CourseOverview are course_id (str),
    while CourseLocator needed.
    '''
    def clean(self, value):
        value = [CourseKey.from_string(v) for v in value]
        return super(ProductModelMultipleChoiceField, self).clean(value)


class ProgramForm(forms.ModelForm):
    products = ProductModelMultipleChoiceField(
        queryset=CourseOverview.objects.filter(product=True),
        required=False,
        label='Shippable or downloadable products'
    )


class ProgramAdmin(admin.ModelAdmin):
    form = ProgramForm
    fields = (
        'products',
    )

    def has_add_permission(self, request, obj=None):
        return False


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
    filter_horizontal = ('programs',)
    # for DjangoMpttAdmin fields = '__all__' doesn't work
    fields = (
        'name', 'slug', 'img', 'description', 'parent', 'url', 'courses', 'programs',
    )

admin.site.register(CourseCategory, CourseCategoryAdmin)
admin.site.register(Program, ProgramAdmin)
