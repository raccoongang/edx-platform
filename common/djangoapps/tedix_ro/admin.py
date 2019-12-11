import datetime
from itertools import chain
import pytz
import time

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportMixin
from import_export.fields import Field
from import_export.formats import base_formats
from import_export.forms import ImportForm
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
    StudentCourseDueDate,
    Question,
    VideoLesson,
)

STUDENT_PARENT_EXPORT_FIELD_NAMES = (
    'username',
    'email',
    'public_name',
    'phone',
    'parent_email',
    'parent_phone',
    'teacher_email',
    'city',
    'school',
    'classroom'
)

INSTRUCTOR_EXPORT_FIELD_NAMES = (
    'username',
    'email',
    'public_name',
    'phone',
    'city',
    'school'
)


admin.site.register(Classroom)



class QuestionInline(admin.TabularInline):
    model = Question
    list_display = ('question_id',)


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ('user', 'course')
    inlines = [QuestionInline]


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        instructors = InstructorProfile.objects.all()
        students = StudentProfile.objects.all()
        parents = ParentProfile.objects.all()
        instance = kwargs.get('instance')
        if instance:
            if isinstance(instance, StudentProfile):
                students = students.exclude(user=instance.user)
            if isinstance(instance, InstructorProfile):
                instructors = instructors.exclude(user=instance.user)
            if isinstance(instance, ParentProfile):
                parents = parents.exclude(user=instance.user)
        users = User.objects.exclude(id__in=set(chain(
            instructors.values_list('user_id', flat=True),
            students.values_list('user_id', flat=True),
            parents.values_list('user_id', flat=True)
        )))
        self.fields['user'].queryset = users


class StudentProfileForm(ProfileForm):
    class Meta:
        model = StudentProfile
        fields = '__all__'


class InstructorProfileForm(ProfileForm):
    class Meta:
        model = InstructorProfile
        fields = '__all__'


class ParentProfileForm(ProfileForm):
    class Meta:
        model = ParentProfile
        fields = '__all__'


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    form = ParentProfileForm
    search_fields = ['user__username', 'user__profile__name']


class InstructorProfileResource(resources.ModelResource):

    school = Field(
        attribute='school__name',
        column_name='school'
    )

    city = Field(
        attribute='school_city__name',
        column_name='city',
    )

    username = Field(
        attribute='user__username',
        column_name='username',
    )

    email = Field(
        attribute='user__email',
        column_name='email',
    )

    public_name = Field(
        attribute='user__profile__name',
        column_name='public_name',
    )

    class Meta:
        model = InstructorProfile
        fields = INSTRUCTOR_EXPORT_FIELD_NAMES
        export_order = INSTRUCTOR_EXPORT_FIELD_NAMES
        import_id_fields = ('email',)
        skip_unchanged = True


@admin.register(InstructorProfile)
class InstructorProfileAdmin(ImportExportModelAdmin):
    form = InstructorProfileForm
    resource_class = InstructorProfileResource
    formats = (
        base_formats.CSV,
        base_formats.JSON,
    )
    search_fields = ['user__username', 'user__profile__name']


class StudentProfileResource(resources.ModelResource):

    school = Field(
        attribute='school__name',
        column_name='school'
    )

    city = Field(
        attribute='school_city__name',
        column_name='city',
    )

    username = Field(
        attribute='user__username',
        column_name='username',
    )

    email = Field(
        attribute='user__email',
        column_name='email',
    )

    public_name = Field(
        attribute='user__profile__name',
        column_name='public_name',
    )
    teacher_email = Field(
        attribute='instructor__user__email',
        column_name='teacher_email'
    )
    classroom = Field(
        attribute='classroom__name',
        column_name='classroom',
    )
    parent_email = Field()
    parent_phone = Field()

    class Meta:
        model = StudentProfile
        fields = STUDENT_PARENT_EXPORT_FIELD_NAMES
        export_order = STUDENT_PARENT_EXPORT_FIELD_NAMES

    def dehydrate_parent_email(self, student_profile):
        return student_profile.parents.all().first().user.email
    
    def dehydrate_parent_phone(self, student_profile):
        return student_profile.parents.all().first().phone


@admin.register(StudentProfile)
class StudentProfileImportExportAdmin(ImportExportModelAdmin):
    resource_class = StudentProfileResource
    formats = (
        base_formats.CSV,
        base_formats.JSON,
    )
    search_fields = ['user__username', 'user__profile__name']


class CityResource(resources.ModelResource):
    schools_name = Field(
        attribute='schools',
        column_name='schools_name'
    )

    class Meta:
        model = City
        fields = ('name', 'schools_name')
        import_id_fields = ('name',)


@admin.register(City)
class CityAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = CityResource
    formats = (
        base_formats.JSON,
    )
    search_fields = ['name']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']


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
        if due_date_utc and student:
            try:
                course_id = CourseKey.from_string(self.cleaned_data.get('course_id'))
                course = CourseOverview.objects.get(id=course_id)
                utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
                if not (course.start < due_date_utc < course.end and utcnow < due_date_utc):
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
    search_fields = ['student__user__username', 'student__user__profile__name', 'course_id']
    date_hierarchy = 'due_date'
    
    def format_date(self, obj):
        return obj.due_date.strftime('%d %b %Y %H:%M')
        
    format_date.short_description = 'Due Date (UTC)'
