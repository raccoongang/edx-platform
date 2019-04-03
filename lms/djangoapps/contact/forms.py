from .models import contactform
from django import forms

class contactforms(forms.ModelForm):

	name = forms.CharField(
		label = 'Full Name',
		required = True,
		min_length = 1,
		error_messages={
			"min_length": "Name must be Atleast Five characters.",
			"required": "Name is required.",
		}
	)

	emailid = forms.CharField(
		label = 'Email-id',
		required = True,
		max_length=75,
		error_messages={
			"required": "Email is required.",
			"max_length" : "Email cannot be more than 75 characters long.",
		}
	)

	phone = forms.CharField(
		label = 'Mobile',
		required = True,
		max_length=13,
		min_length = 10,
		error_messages={
			"min_length": "Mobile must be atleast 10 characters.",
			"required": "Mobile is required.",
			"max_length" : "Mobile cannot be more than 13 characters long.",
		}
	)


	formmsg = forms.CharField(
		label = 'Message',
		min_length = 20,
		required=True,
		error_messages={
			"min_length": "Message must be atleast 150 characters.",
			"required": "Message is required.",
		}
	)

	ENQUIRY_TYPE = (
        ('1', 'Medical Content'),
        ('2', 'Technical'),
        ('3', 'Certificates'),
        ('4', 'General'),
        ('5', 'Sales & Partnership')
    )

	enquiry_type = forms.ChoiceField(
    	label='User Type',
    	widget=forms.Select(),
    	choices=ENQUIRY_TYPE,
    	required=True,
    	error_messages={
			"required": "Please select enquiry option.",
		}
	)

	def clean(self, *args, **kwargs):
		name = self.cleaned_data["name"]
		emailid = self.cleaned_data["emailid"]
		phone = self.cleaned_data["phone"]
		enquiry_type = self.cleaned_data["enquiry_type"]
		formmsg = self.cleaned_data["formmsg"]

	class Meta(object):
		model = contactform
		fields = ('name','emailid','enquiry_type','message')
