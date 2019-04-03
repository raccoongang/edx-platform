from django.shortcuts import render, HttpResponse
from .models import webform
from django.core.exceptions import ObjectDoesNotExist
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys import InvalidKeyError

# Create your views here.
def webformdetails(courseid):
	course_key = CourseKey.from_string(courseid)
	try:
		getDetails = webform.objects.get(courseid=courseid)
	except ObjectDoesNotExist:
		getDetails = None
	return getDetails

def feedback_form_link(courseid):
	try:
		getDetails = webform.objects.get(courseid=courseid)
	except ObjectDoesNotExist:
		getDetails = None
	return getDetails