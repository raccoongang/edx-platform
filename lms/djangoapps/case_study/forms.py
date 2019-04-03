from lms.djangoapps.case_study.models import case_study_abstracts
from django import forms
from django.conf import settings

class case_study_abstracts_form(forms.ModelForm):
    title = forms.CharField(
        label = 'Title',
        required = True,
        error_messages={
            "required": "Title is required.",
        }
    )

    description = forms.CharField(
        label = 'Description',
        required = True,
        error_messages={
            "required": "Description is required.",
        }
    )

    uploaded_file = forms.CharField(
        label = 'Upload file',
        required = True,
        error_messages={
            "required": "File is required.",
        }
    )

    USER_TYPE = (
        ('dr', 'Doctor'),
        ('prof', 'Professor'),
        ('std', 'Student'),
        ('team', 'Team')
    )
    user_type = forms.ChoiceField(
        label='User Type',
        widget=forms.Select(),
        choices=USER_TYPE,
        required=True,
        error_messages={
            "required": "Please select user type.",
        }
    )

    CASE_STUDY_TYPE = (
        ('Observational (non-experimental) studies',
            (
                ('chrt-stds', 'Cohort studies'),
                ('case-cntrl', 'Case control studies'),
                ('rdbs', 'Routine-data-based studies'),
                ('drs', 'Dose-response studies'),
            )
        ),
        ('Intervention (experimental) studies',
            (
                ('cl', 'Clinical trials'),
                ('fli', 'Field trials(individual level)'),
                ('fla', 'Field trials(aggregated level)')
            )
        ),        
    )

    case_study_type = forms.ChoiceField(
        label='Case Study Type',
        widget=forms.Select(),
        choices=CASE_STUDY_TYPE,
        required=True,
        error_messages={
            "required": "Please select case study type.",
        }
    )

    def clean(self):
        title = self.cleaned_data['title']
        description = self.cleaned_data['description']
        user_type = self.cleaned_data['user_type']

    class Meta:
        model = case_study_abstracts
        fields = ('title','description','uploaded_file','user_type','case_study_type')
