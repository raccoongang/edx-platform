import datetime
import pytz
import time

from django import forms
from django.contrib import admin
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


class StudentCourseDueDateForm(forms.ModelForm):

    class Meta:
        model = StudentCourseDueDate
        fields = '__all__'

    def clean(self):
        super(StudentCourseDueDateForm, self).clean()
        student = self.cleaned_data.get('student')
        due_date = self.cleaned_data.get('due_date')

        due_date_utc = datetime.datetime.fromtimestamp(time.mktime(
            due_date.timetuple()),
            tz=pytz.utc
        )

        try:
            course_id = CourseKey.from_string(self.cleaned_data.get('course_id'))
            course = CourseOverview.objects.get(id=course_id)
            if not course.enrollment_start < due_date_utc < course.enrollment_end:
                self.add_error('due_date', 'This due date is not valid for the course: {}'.format(course_id))
        except CourseOverview.DoesNotExist:
            raise forms.ValidationError("Course does not exist")
        except InvalidKeyError:
            self.add_error('course_id', 'Invalid CourseKey')

        return self.cleaned_data


@admin.register(StudentCourseDueDate)
class StudentCourseDueDateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_id', 'due_date')
    form = StudentCourseDueDateForm
