from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from student.models import (
    PasswordHistory,
    Registration,
    UserProfile
)
from student.views.management import compose_and_send_activation_email

from tedix_ro.models import City, School, StudentProfile, CLASSROOM_CHOICES, InstructorProfile, ParentProfile

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

    def clean_parent_email(self):
        """
        Validate parent email
        """
        parent_email = self.cleaned_data['parent_email']
        user = User.objects.filter(email=parent_email).first()
        if user and getattr(user, 'studentprofile', None):
            raise forms.ValidationError('This email belongs to an existing Student profile')
        if user and not getattr(user, 'parentprofile', None):
            raise forms.ValidationError('User with this email is not registered as parent')
        return parent_email

    def save(self, commit=True):
        if self.cleaned_data['role'] == 'student':
            # Make user for parent
            parent_user = User(
                username=self.cleaned_data['parent_email'].split('@')[0],
                email=self.cleaned_data['parent_email'],
                is_active=False
            )
            password = User.objects.make_random_password()
            parent_user.set_password(password)
            parent_user.save()

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

            # Send activation email to the parent as well
            compose_and_send_activation_email(parent_user, profile, registration)

            instance = super(StudentRegisterForm, self).save(commit)
            instance.parent_user = parent_user
            instance.school_city = self.cleaned_data['school_city']
            instance.school = self.cleaned_data['school']
            instance.parent_phone = self.cleaned_data['parent_phone']
            instance.password = password
            return instance

        return super(StudentRegisterForm, self).save(commit)


    class Meta(object):
        model = StudentProfile
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'instructor', 'school_city', 'school', 'classroom')
        serialization_options = {
            'role': {
                'default': 'student',
                'include_default_option': True
            }
        }


class InstructorRegisterForm(RegisterForm):
    """
    The fields on this form are derived from the InstructorProfile model
    """
    class Meta(object):
        model = InstructorProfile
        fields = ('role', 'phone', 'school_city', 'school')
