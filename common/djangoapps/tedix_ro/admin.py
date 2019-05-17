import datetime
import pytz
import time

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from tedix_ro.models import (
    City,
    School,
    ParentProfile,
    StudentProfile,
    InstructorProfile,
    Classroom,
    StudentCourseDueDate
)


admin.site.register(InstructorProfile)
admin.site.register(StudentProfile)
admin.site.register(ParentProfile)
admin.site.register(Classroom)


class CityResource(resources.ModelResource):

    class Meta:
        model = City
        fields = ('name',)
        import_id_fields = ('name',)


@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    resource_class = CityResource
    formats = (
        base_formats.CSV,
        base_formats.JSON,
    )


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CustomAdminSplitDateTime(AdminSplitDateTime):

    def decompress(self, value):
        if value:
            return [value.date(), value.time()]
        return [None, None]


class StudentCourseDueDateForm(forms.ModelForm):

    class Meta:
        model = StudentCourseDueDate
        fields = '__all__'
        help_texts = {
            'due_date': 'Time in UTC',
        }
    def __init__(self, *args, **kwargs):
        super(StudentCourseDueDateForm, self).__init__(*args, **kwargs)
        self.fields['due_date'].widget = CustomAdminSplitDateTime()
        self.fields['student'].queryset = StudentProfile.objects.filter(user__is_active=True)
    
    def clean_due_date(self):
        data = self.cleaned_data['due_date'].replace(tzinfo=pytz.UTC)
        return data

    def clean(self):
        super(StudentCourseDueDateForm, self).clean()
        student = self.cleaned_data.get('student')
        due_date_utc = self.cleaned_data.get('due_date')
        try:
            course_id = CourseKey.from_string(self.cleaned_data.get('course_id'))
            course = CourseOverview.objects.get(id=course_id)
            utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            if not (course.enrollment_start < due_date_utc < course.enrollment_end and utcnow < due_date_utc):
                self.add_error('due_date', 'This due date is not valid for the course: {}'.format(course_id))
        except CourseOverview.DoesNotExist:
            raise forms.ValidationError("Course does not exist")
        except InvalidKeyError:
            self.add_error('course_id', 'Invalid CourseKey')

        return self.cleaned_data


@admin.register(StudentCourseDueDate)
class StudentCourseDueDateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_id', 'format_date')
    form = StudentCourseDueDateForm
    
    def format_date(self, obj):
        return obj.due_date.strftime('%d %b %Y %H:%M')
        
    format_date.short_description = 'Due Date (UTC)'
