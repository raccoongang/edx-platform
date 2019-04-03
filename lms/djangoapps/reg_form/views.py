from django.shortcuts import render, HttpResponse
from .models import extrafields
from django.core.exceptions import ObjectDoesNotExist
from student.models import UserProfile
from django.contrib.auth.models import User

# Create your views here.
def ajaxform(request):
	if request.method == 'POST':

		usertype = request.POST['usertype']

		return HttpResponse("registration/reg_usertype.html",{'usertype': usertype}
    	)

def userdetails(userid):
	try:
		getDetails = extrafields.objects.get(user_id=userid)
	except ObjectDoesNotExist:
		getDetails = None

	return getDetails

def getuserfullprofile(userid):
	try:
		getDetails = UserProfile.objects.get(user_id=userid)
	except ObjectDoesNotExist:
		getDetails = None

	return getDetails

def get_authuser(userid):
	try:
		getDetails = User.objects.get(id=userid)
	except ObjectDoesNotExist:
		getDetails = None

	return getDetails