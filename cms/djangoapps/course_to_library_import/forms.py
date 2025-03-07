"""
This module contains the form for the CourseToLibraryImport model.
"""

from django import forms
from django.contrib.auth import get_user_model

from .models import CourseToLibraryImport


User = get_user_model()


class CourseToLibraryImportForm(forms.ModelForm):
    """
    Form for importing a course to a library.
    """

    class Meta:
        model = CourseToLibraryImport
        fields = '__all__'

    user = forms.IntegerField(min_value=1, label='User ID')

    def clean_user(self):
        """
        Validate the user ID.
        """

        user_id = self.cleaned_data['user']
        if not User.objects.filter(id=user_id).exists():
            raise forms.ValidationError('User does not exist')
        return user_id
