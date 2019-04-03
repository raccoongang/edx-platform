from django.shortcuts import render
from .models import hcspecializations
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def hcSpecName(specId):
	specname = ''
	try:
		getDetails = hcspecializations.objects.get(id=specId)
		specname = getDetails.name
	except ObjectDoesNotExist:
		getDetails = None
		
	return specname
