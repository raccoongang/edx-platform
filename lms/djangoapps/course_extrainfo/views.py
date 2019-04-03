from django.shortcuts import render
from .models import course_extrainfo
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def course_ctype(speczId):
    from django.core.exceptions import ObjectDoesNotExist
    speczname = ''
    ctype = ''
    try:
        getDetails = course_extrainfo.objects.get(course_id=speczId)
        speczname = getDetails.course_type
    except ObjectDoesNotExist:
        getDetails = None

    if speczname == '1' :
    	ctype = 'course'
    else:
    	ctype = 'courseware'
    return ctype

def course_ctype_number(speczId):
    from django.core.exceptions import ObjectDoesNotExist
    speczname = ''
    ctype = ''
    try:
        getDetails = course_extrainfo.objects.get(course_id=speczId)
        speczname = getDetails.course_type
    except ObjectDoesNotExist:
        getDetails = None
    return speczname
