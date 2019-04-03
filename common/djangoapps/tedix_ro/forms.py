from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from student.models import (
    PasswordHistory,
    Registration,
    UserProfile
)

from tedix_ro.models import City, School, StudentProfile, CLASSROOM_CHOICES, InstructorProfile, ParentProfile

ROLE_CHOICES = (
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
    classroom = forms.ChoiceField(
        label='Classroom', choices=CLASSROOM_CHOICES,
        error_messages={
            'required': 'Please select your classroom.'
        }
    )
    parent_phone = forms.CharField(label='Parent Phone Number', error_messages={
        'required': 'Please enter your parent phone number.',
        'min_length': 9,
        'max_length': 15,
    })
    parent_email = forms.EmailField(label='Parent Email', error_messages={
        'required': 'Please enter your parent email.'
    })
    instructor = forms.ModelChoiceField(
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
            parent_user, created = User.objects.get_or_create(
                username=parent_email.split('@')[0],
                email=parent_email,
                defaults={'is_active': False}
            )
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
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'instructor', 'school_city', 'school', 'classroom')
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
