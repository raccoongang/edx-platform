import datetime
import json
import pytz
import re
import time

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm
from django.utils import six, timezone
from django.utils.encoding import force_text

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from student.forms import AccountCreationForm, CourseEnrollmentAllowed
from student.models import (
    PasswordHistory,
    Registration,
    UserProfile
)
from tedix_ro.models import (
    City,
    School,
    StudentProfile,
    InstructorProfile,
    ParentProfile,
    Classroom,
    phone_validator
)


ROLE_CHOICES = (
    ('student', 'Student'),
    ('instructor', 'Instructor'),
)


FORM_FIELDS_MAP = {
    # fields for InstructorImportValidationForm
    'city': 'school_city',
    'public_name': 'name',

    # fields for StudentImportRegisterForm
    'teacher_email': 'instructor',

    # fields for SchoolImportValidationForm
    'city_name': 'city',
    'school_name': 'name'
}


def get_tedix_registration_form(role):
    if role == 'instructor':
        return InstructorRegisterForm
    if role == 'student':
        return StudentRegisterForm


def get_username_by_email(email):
    """
    Return a unique username by email
    """
    username = email.split('@')[0]
    x = 1
    new_username = username
    while User.objects.filter(username=new_username).exists():
        new_username = "{0}_{1}".format(username, x)
        x += 1
    return new_username


class RegisterForm(ModelForm):
    """
    Abstract register form
    """
    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)
    phone = forms.CharField(label='Phone Number', error_messages={
        'required': 'Please enter your phone number.'
    })
    school_city = forms.ModelChoiceField(
        label='City', queryset=City.objects.all(),
        error_messages={
            'required': 'Please select your city.'
        }
    )
    school = forms.ModelChoiceField(
        label='School', queryset=School.objects.all(),
        error_messages={
            'required': 'Please select your school.'
        }
    )


class StudentRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the StudentProfile and ParentProfile models
    """
    admin_import_action = False
    classroom = forms.ModelChoiceField(
        label='Classroom', queryset=Classroom.objects.all(),
        error_messages={
            'required': 'Please select your classroom.'
        }
    )
    parent_phone = forms.CharField(
        label='Parent Phone Number',
        validators=[phone_validator],
        error_messages={
            'required': 'Please enter your parent phone number.',
            'min_length': 9,
            'max_length': 15,
        }
    )
    parent_email = forms.EmailField(label='Parent Email', error_messages={
        'required': 'Please enter your parent email.'
    })
    instructor = forms.ModelChoiceField(
        required=False,
        label='Teacher',
        queryset=InstructorProfile.objects.filter(user__is_staff=True, user__is_active=True),
        error_messages={
            'required': 'Please select your teacher.'
        }
    )
    phone = forms.CharField(label='Phone Number', error_messages={
        'required': 'Please enter your phone number.',
        'min_length': 10,
        'max_length': 15,
    })

    def clean_phone(self):
        """
        Validate phone number
        """
        # TODO: there is a validator field, remove the additional validation of
        # the length of the phone number in the future
        phone = self.cleaned_data['phone']
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError('The phone number length must be from 10 to 15 digits.')
        return phone


    def clean_parent_email(self):
        """
        Validate parent email
        """
        parent_email = self.cleaned_data['parent_email']
        if parent_email == self.data['email']:
            raise forms.ValidationError('Student and parent emails must be different.')
        user = User.objects.filter(email=parent_email).first()
        if user and (getattr(user, 'studentprofile', None) or not getattr(user, 'parentprofile', None)) or user and not user.is_active:
            raise forms.ValidationError('Parent email you entered belongs to an existing profile.')
        return parent_email
    
    def clean_parent_phone(self):
        parent_email = self.cleaned_data.get('parent_email', '')
        parent_phone = self.cleaned_data['parent_phone']
        user = User.objects.filter(email=parent_email).first() if parent_email else None
        # TODO: there is a validator field, remove the additional validation of
        # the length of the phone number in the future
        if len(parent_phone) < 10 or len(parent_phone) > 15:
            raise forms.ValidationError('The parent phone number length must be from 10 to 15 digits.')
        if user and getattr(user, 'parentprofile', None) and parent_phone != user.parentprofile.phone:
            raise forms.ValidationError('Parent phone number you entered is wrong.')
        student_phone = self.cleaned_data.get('phone')
        if parent_phone == student_phone:
            raise forms.ValidationError('Student and parent phone numbers must be different.')
        return parent_phone

    def save(self, commit=True):
        if self.cleaned_data['role'] == 'student':
            # Make user for parent
            parent_email = self.cleaned_data['parent_email']
            parent_user = User.objects.filter(email=parent_email).first()
            if parent_user:
                created = False
            else:
                parent_user = User.objects.create(
                    username=get_username_by_email(parent_email),
                    email=parent_email,
                    is_active=False if not self.admin_import_action else True
                )
                created = True
            if created:
                # add this account creation to password history
                # NOTE, this will be a NOP unless the feature has been turned on in configuration
                password_history_entry = PasswordHistory()
                password_history_entry.create(parent_user)

                # Make UserProfile
                profile = UserProfile(user=parent_user)
                profile.save()

                # Create registry for parent
                registration = Registration()
                registration.register(parent_user)
            else:
                profile = parent_user.profile
                registration = None

            instance = super(StudentRegisterForm, self).save(commit)
            instance.parent_user = parent_user
            instance.profile = profile
            instance.registration = registration
            instance.parent_phone = self.cleaned_data['parent_phone']
            return instance

        return super(StudentRegisterForm, self).save(commit)


    class Meta(object):
        model = StudentProfile
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'school_city', 'school', 'instructor', 'classroom')
        serialization_options = {
            'role': {
                'default': 'student',
                'include_default_option': True
            },
            'phone': {
                'field_type': 'text'
            },
            'parent_phone': {
                'field_type': 'text'
            }
        }


class InstructorRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the InstructorProfile model
    """
    class Meta(object):
        model = InstructorProfile
        fields = ('role', 'phone', 'school_city', 'school')
        serialization_options = {
            'phone': {
                'field_type': 'text'
            }
        }

class CustomDateTimeField(forms.DateTimeField):

    def to_python(self, value):
        value = super(forms.DateTimeField, self).to_python(value)
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=pytz.UTC)
        return value

class CourseMultipleModelChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return u"{}".format(obj.display_name)

    def _check_values(self, value):
        """
        Given a list of possible PK values, returns a QuerySet of the
        corresponding objects. Raises a ValidationError if a given value is
        invalid (not a valid PK, not in the queryset, etc.)
        """
        key = self.to_field_name or 'pk'
        # deduplicate given values to avoid creating many querysets or
        # requiring the database backend deduplicate efficiently.
        try:
            value = frozenset(value)
        except TypeError:
            # list of lists isn't hashable, for example
            raise ValidationError(
                self.error_messages['list'],
                code='list',
            )
        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_pk_value'],
                    code='invalid_pk_value',
                    params={'pk': pk},
                )
        qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set(force_text(getattr(o, key)) for o in qs)
        error_course_list = list()
        for val in value:
            if force_text(val) not in pks:
                course = CourseOverview.objects.filter(id=val).first()
                error_course_list.append(course.display_name if course else val)
        if error_course_list:
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': '", "'.join(error_course_list)},
            )
        return qs


class StudentMultipleModelChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return u"{}".format(obj.user.profile.name) if obj.user.profile.name else obj.user.username


class StudentEnrollForm(forms.Form):
    courses = CourseMultipleModelChoiceField(queryset=CourseOverview.objects.none())
    students = StudentMultipleModelChoiceField(queryset=StudentProfile.objects.none())
    due_date = CustomDateTimeField(
        label='Due Date (UTC):',
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime',
            'autocomplete': 'off'
        })
    )
    send_to_students = forms.BooleanField(required=False, label='Notify Student(s) via e-mail')
    send_to_parents = forms.BooleanField(required=False, label='Notify Parent(s) via e-mail')
    send_sms = forms.BooleanField(required=False, label='Notify Parent(s) via SMS')

    def __init__(self, *args, **kwargs):
        courses = kwargs.pop('courses')
        students = kwargs.pop('students')
        super(StudentEnrollForm, self).__init__(*args, **kwargs)
        self.fields['courses'].queryset = courses
        self.fields['courses'].error_messages={
            'invalid_choice': u'The enrollment end date has passed. The following courses are no longer available for enrollment: "%(value)s".',
        }
        self.fields['students'].queryset = students

    def clean_due_date(self):
        due_date_utc = self.cleaned_data['due_date']
        courses  = self.cleaned_data.get('courses')
        if courses:
            utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            error_course_list = list()
            for course in courses:
                if course.end:
                    if due_date_utc < course.start or due_date_utc > course.end or due_date_utc < utcnow:
                        error_course_list.append(course.display_name)
                elif due_date_utc < course.start or due_date_utc < utcnow:
                    error_course_list.append(course.display_name)
            if error_course_list:
                self.add_error('due_date', u'This due date is not valid for the following courses: "{}".'.format('", "'.join(error_course_list)))
        return due_date_utc


class ProfileImportForm(forms.Form):
    file_to_import = forms.FileField()
    file_format = forms.ChoiceField(choices=[
        ('', '------'),
        ('csv', 'csv'),
        ('json', 'json')
    ])

    def clean(self):
        cleaned_data = super(ProfileImportForm, self).clean()
        file_to_import = cleaned_data['file_to_import']
        file_format = cleaned_data['file_format']
        if not file_to_import.name.endswith('.{}'.format(file_format)):
            self.add_error('file_format', 'The file you are going to import has another extension.')
        return cleaned_data


class CityImportForm(forms.Form):
    file_to_import = forms.FileField()

    def clean_file_to_import(self):
        file_to_import = self.cleaned_data['file_to_import']
        if not file_to_import.name.endswith('.json'):
            raise ValidationError('The file extension is not supported. Please use a file with .json extension.')
        try:
            file_data = json.loads(file_to_import.read())
        except Exception as e:
            raise ValidationError('Oops! Something went wrong. Please check that the file structure is correct.')
        file_to_import.seek(0)
        return file_to_import


class StudentProfileImportForm(ProfileImportForm):
    send_payment_link = forms.BooleanField(required=False)


class AccountImportValidationForm(AccountCreationForm):

    def clean_email(self):
        """ Enforce email restrictions (if applicable) """
        email = self.cleaned_data["email"]
        if settings.REGISTRATION_EMAIL_PATTERNS_ALLOWED is not None:
            # This Open edX instance has restrictions on what email addresses are allowed.
            allowed_patterns = settings.REGISTRATION_EMAIL_PATTERNS_ALLOWED
            # We append a '$' to the regexs to prevent the common mistake of using a
            # pattern like '.*@edx\\.org' which would match 'bob@edx.org.badguy.com'
            if not any(re.match(pattern + "$", email) for pattern in allowed_patterns):
                # This email is not on the whitelist of allowed emails. Check if
                # they may have been manually invited by an instructor and if not,
                # reject the registration.
                if not CourseEnrollmentAllowed.objects.filter(email=email).exists():
                    raise ValidationError(_("Unauthorized email address."))
        return email

    def clean(self):
        cleaned_data = super(AccountImportValidationForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if not User.objects.filter(email=email, username=username).exists() and User.objects.filter(username=username).exists():
            self.add_error('username', u'Public Username "{}" already exists.'.format(username))


class InstructorImportValidationForm(InstructorRegisterForm):

    def __init__(self, *args, **kwargs):
        super(InstructorImportValidationForm, self).__init__(*args, **kwargs)
        self.fields['school_city'].to_field_name = 'name'
        self.fields['school_city'].error_messages.update({'invalid_choice': "Such city doesn't exists in DB",})
        self.fields['school'].to_field_name = 'name'
        self.fields['school'].error_messages.update({'invalid_choice': "Such school doesn't exists in DB"})

    def clean(self):
        cleaned_data = super(InstructorImportValidationForm, self).clean()
        school = cleaned_data.get('school')
        school_city = cleaned_data.get('school_city')
        if school_city and school and school.city != school_city:
            self.add_error('school', u'School {} is not in the city {}.'.format(school.name, school_city.name))

    def exists(self, data):
        return InstructorProfile.objects.filter(user__email=data['email']).exists()
    
    def update(self, data):
        email = data['email']
        school_city = self.cleaned_data['school_city']
        school = self.cleaned_data['school']
        if InstructorProfile.objects.filter(
            user__email=email,
            school_city=school_city, school=school):
            return 'skipped'
        InstructorProfile.objects.filter(user__email=email).update(school_city=school_city, school=school)
        return 'updated'


class StudentImportRegisterForm(StudentRegisterForm):

    admin_import_action = True

    def __init__(self, *args, **kwargs):
        super(StudentImportRegisterForm, self).__init__(*args, **kwargs)
        self.fields['school_city'].to_field_name = 'name'
        self.fields['school_city'].error_messages.update({'invalid_choice': "Such city doesn't exists in DB",})
        self.fields['school'].to_field_name = 'name'
        self.fields['school'].error_messages.update({'invalid_choice': "Such school doesn't exists in DB"})
        self.fields['classroom'].to_field_name = 'name'
        self.fields['instructor'].to_field_name = 'user__email'
        self.fields['instructor'].error_messages.update({'invalid_choice': "Such instructor doesn't exists in DB"})

    def exists(self, data):
        return StudentProfile.objects.filter(user__email=data['email']).exists()
    
    def update(self, data):
        email = data['email']
        school_city = self.cleaned_data['school_city']
        school = self.cleaned_data['school']
        instructor = self.cleaned_data['instructor']
        if StudentProfile.objects.filter(
            user__email=email,
            school_city=school_city, school=school, instructor=instructor):
            return 'skipped'
        StudentProfile.objects.filter(user__email=email).update(school_city=school_city, school=school, instructor=instructor)
        return 'updated'
    
    def clean(self):
        cleaned_data = super(StudentImportRegisterForm, self).clean()
        school = cleaned_data.get('school')
        school_city = cleaned_data.get('school_city')
        instructor = cleaned_data.get('instructor')
        if school_city and school and school.city != school_city:
            self.add_error('school', u'School {} is not in the city {}.'.format(school.name, school_city.name))
        if instructor and instructor.school != school:
            self.add_error('instructor', "Specified instructor belongs to another school")
        return cleaned_data


class SchoolImportValidationForm(ModelForm):

    class Meta(object):
        model = School
        fields = ('name', 'city', 'school_type')

    def __init__(self, *args, **kwargs):
        super(SchoolImportValidationForm, self).__init__(*args, **kwargs)
        self.fields['city'].to_field_name = 'name'
        self.fields['school_type'].error_messages.update({
            'required': "The value is invalid. Valid school types are 'Privata' and 'Publica'.",
        })


    def exists(self, name, city_name):
        city = City.objects.filter(name=city_name).first()
        return School.objects.filter(name=name, city=city).exists()

    def update(self, school_name, city_name, school_type):
        city = City.objects.filter(name=city_name).first()
        if School.objects.filter(name=school_name, city=city, school_type=school_type).exists():
            return 'skipped'
        School.objects.filter(name=school_name, city=city).update(school_type=school_type)
        return 'updated'

    def clean(self):
        """
        Override clean to skip unique validation for fields `name` and `city`
        so as not to raise error but update the instance
        """
        return self.cleaned_data


class CityImportValidationForm(ModelForm):

    class Meta(object):
        model = City
        fields = ('name',)

    def exists(self, name):
        return City.objects.filter(name=name).exists()

    def clean(self):
        """
        Override clean to skip unique validation for field `name`
        so as not to raise error but update the instance
        """
        return self.cleaned_data
