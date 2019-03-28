from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from tedix_ro.models import City, School, StudentProfile, CLASSROOM_CHOICES, InstructorProfile

ROLE_CHOICES = (
    ('', ''),

    ('student', 'Student'),
    ('instructor', 'Instructor'),
)


def get_tedix_registration_form(role):
    print('!!!', role)
    if role == 'instructor':
        return InstructorRegisterForm
    if role == 'student':
        return StudentRegisterForm


class RegisterForm(ModelForm):
    """
    Abstract register form
    """
    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)
    phone = forms.CharField(label='Phone number')
    school_city = forms.ModelChoiceField(label='City', queryset=City.objects.all())
    school = forms.ModelChoiceField(label='School', queryset=School.objects.all())

    def clean(self):
        data = self.cleaned_data
        print('!!! data', data)
        data['city'] = data['school_city']
        del data['city']
        return data


class StudentRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the StudentParent model
    """
    classroom = forms.ChoiceField(label='Classroom', choices=CLASSROOM_CHOICES)
    parent_phone = forms.CharField(label='Parent phone number')
    parent_email = forms.EmailField(label='Parent email')
    instructor = forms.ModelChoiceField(label='Teacher', queryset=InstructorProfile.objects.all())

    class Meta(object):
        model = StudentProfile
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'instructor', 'school_city', 'school', 'classroom')


class InstructorRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the StudentParent model
    """
    class Meta(object):
        model = InstructorProfile
        fields = ('role', 'phone', 'school_city', 'school')
