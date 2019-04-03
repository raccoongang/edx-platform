from .models import extrafields
from django import forms
from django.conf import settings
from lms.djangoapps.specialization.models import specializations
from lms.djangoapps.hcspecialization.models import hcspecializations
#from lms.djangoapps.country.models import countries, states, cities

class regextrafields(forms.ModelForm):

    phone = forms.CharField(
        label = 'Contact Number *',
        min_length = 10,
        required=True,
        error_messages={
            "min_length": "Phone number must be atleat 10 Digits",
            "required" : "enter your number"
        }
    )

    rpincode = forms.CharField(
        label = 'Pincode *',
        min_length = 1,
        required=True,
        error_messages={
            "required":"Please enter your pincode/zipcode/postal-code"
        }
    )

    rcountry = forms.CharField(
        min_length = 1,
        error_messages={
            "min_length": "Please enter your country",
            "required" : "enter your country"
        }
    )
    rstate = forms.CharField(
        label = 'State',
        min_length = 1,
        error_messages={
            "min_length": "Please enter your state",
            "required" : "enter your state"
        }
    )
    rcity = forms.CharField(
        label = 'City',
        min_length = 1,
        error_messages={
            "min_length": "Please enter your city",
            "required" : "enter your city"
        }
    )

    address = forms.CharField(
        label = 'Address',
        required=False
    )

    reg_num = forms.CharField(
        label='Medical Registration Number',
        required=False
    )

    specialization = forms.ModelChoiceField(
        queryset=specializations.objects.all(),
        empty_label="select your specialization",
        label='Specialization',
        required=False
    )
    
    hcspecialization = forms.ModelChoiceField(
        queryset=hcspecializations.objects.all(),
        empty_label="select your specialization",
        label='Health care specialization',
        required=False
    )
        
    USER_TYPE = (
        ('', 'Select user type'),
        ('dr', 'Doctor'),
        ('ms', 'Medical Student'),
        ('hc', 'Health Care Proffessional'),
        ('u', 'User'),
    )

    user_type = forms.ChoiceField(
        label='User Type *',
        choices=USER_TYPE,
        required=True,
        error_messages={
            "required": "Please select user type"
        }
    )

    # regcountry = forms.ModelChoiceField(
    #     queryset=countries.objects.all(),
    #     empty_label="select your country",
    #     label='Country',
    #     required=True
    # )

    # regstate = forms.ModelChoiceField(
    #     queryset=states.objects.all(),
    #     empty_label="select your state",
    #     label='States'
    # )

    # regcity = forms.ModelChoiceField(
    #     queryset=cities.objects.all(),
    #     empty_label="select your city",
    #     label='City'
    # )


    # def clean(self, data=None, *args, **kwargs):
    #     reg_num = self.cleaned_data["reg_num"]

    class Meta(object):
        model = extrafields
        fields = ('phone','user_type','reg_num','specialization','hcspecialization','rpincode', 'rcountry','rstate', 'rcity','address')


    def __init__(self, data=None, *args, **kwargs):
        super(regextrafields, self).__init__(data, *args, **kwargs)
        # if data and data.get('regcountry') == '101':
        #     self.fields['regstate'].required = True
        #     self.fields['regstate'].error_messages = {'required': 'Please select your state'}
        #     self.fields['regcity'].required = True
        #     self.fields['regcity'].error_messages = {'required': 'Please select your city'}
            