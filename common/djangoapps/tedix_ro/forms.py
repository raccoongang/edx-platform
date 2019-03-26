from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from tedix_ro.models import StudentParent, City, School

CLASSROOM_CHOICES = (
    ('', ''),

    ('7A', '7A'),
    ('7B', '7B'),
    ('7C', '7C'),
    ('7D', '7D'),

    ('8A', '8A'),
    ('8B', '8B'),
    ('8C', '8C'),
    ('8D', '8D'),
)

ROLE_CHOICES = (
    ('', ''),

    ('student', 'Student'),
    ('instructor', 'Instructor'),
)


class ExtraRegisterForm(ModelForm):
    """
    The fields on this form are derived from the StudentParent model
    """
    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)
    classroom = forms.ChoiceField(label='Classroom', choices=CLASSROOM_CHOICES)
    phone = forms.CharField(label='Phone number')
    parent_phone = forms.CharField(label='Parent phone number')
    parent_email = forms.CharField(label='Parent email')
    teacher = forms.ModelChoiceField(label='Teacher', queryset=User.objects.filter(is_staff=True, is_superuser=False))
    city = forms.ModelChoiceField(label='City', queryset=City.objects.all())
    school = forms.ModelChoiceField(label='School', queryset=School.objects.all())

    class Meta(object):
        model = StudentParent
        fields = ('role', 'phone', 'parent_email', 'parent_phone', 'teacher', 'city', 'school', 'classroom')
