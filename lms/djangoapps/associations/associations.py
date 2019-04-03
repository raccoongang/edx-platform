from django.http import Http404
from django.conf import settings
from edxmako.shortcuts import render_to_string
from microsite_configuration import microsite

from organizations import data, serializers

#from . import associations

def get_organizations():
    """
    Retrieves the active organizations managed by the system
    """
    return data.fetch_organizations()




