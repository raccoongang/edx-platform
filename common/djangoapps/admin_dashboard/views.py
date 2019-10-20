"""
Views For Admin Dashboard
"""

from student.models import UserSites
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from collections import defaultdict
from django.urls import reverse
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_protect, csrf_exempt


def index(request, template_name="/admin_dashboard/index.html"):
    usersites = UserSites.objects.all()

    page = request.GET.get('page', 1)

    paginator = Paginator(usersites, 50)
    try:
        new_usersites = paginator.page(page)
    except PageNotAnInteger:
        new_usersites = paginator.page(1)
    except EmptyPage:
        new_usersites = paginator.page(paginator.num_pages)

    return render_to_response(template_name, {'userssites': new_usersites})

@csrf_exempt
def add_users(request, template_name="/admin_dashboard/add-users.html"):
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    subdoamins = list(Site.objects.all())

    context = {'create_bulk_users': reverse('create_bulk_users'),
               'subdomains': subdoamins}

    return render_to_response(template_name, context)
