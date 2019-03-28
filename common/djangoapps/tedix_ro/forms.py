from django import forms
from django.forms import ModelForm

from tedix_ro.models import City, School, StudentProfile, CLASSROOM_CHOICES, InstructorProfile

ROLE_CHOICES = (
    ('', ''),

    ('student', 'Student'),
    ('instructor', 'Instructor'),
)


def get_tedix_registration_form(role):
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


class StudentRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the StudentProfile and ParentProfile models
    """
    classroom = forms.ChoiceField(label='Classroom', choices=CLASSROOM_CHOICES)
    parent_phone = forms.CharField(label='Parent phone number', error_messages={
        'required': 'Please enter parent phone number',
        'min_length': 9,
        'max_length': 15,
    })
    parent_email = forms.EmailField(label='Parent email')
    instructor = forms.ModelChoiceField(
        label='Teacher',
        queryset=InstructorProfile.objects.filter(user__is_staff=True, user__is_active=True),
    )

    def save(self, commit=True):
        print('save...', self.cleaned_data)
        return super(StudentRegisterForm, self).save(commit)

    class Meta(object):
        model = StudentProfile
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'instructor', 'school_city', 'school', 'classroom')


class InstructorRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the InstructorProfile model
    """
    class Meta(object):
        model = InstructorProfile
        fields = ('role', 'phone', 'school_city', 'school')
