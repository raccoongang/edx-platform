import logging
import json
import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,HttpResponseRedirect
)
from django.template import RequestContext, Template, loader, context
from django.shortcuts import redirect
from django.http import HttpRequest
from django_countries import countries
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import ugettext as _

from django.views.decorators.http import require_http_methods
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from openedx.core.djangoapps.lang_pref.api import released_languages, all_languages
from edxmako.shortcuts import render_to_response
from microsite_configuration import microsite

from openedx.core.djangoapps.external_auth.login_and_register import (
    login as external_auth_login,
    register as external_auth_register
)

from student.models import UserProfile
from student.views import (
    signin_user as old_login_view,
    register_user as old_register_view
)
from lms.djangoapps.contact.models import contactform
from lms.djangoapps.contact.forms import contactforms

from student.helpers import get_next_url_for_login_page
import third_party_auth
from third_party_auth import pipeline
from third_party_auth.decorators import xframe_allow_whitelisted
from util.bad_request_rate_limiter import BadRequestRateLimiter

from openedx.core.djangoapps.user_api.accounts.api import request_password_change
from openedx.core.djangoapps.user_api.errors import UserNotFound
from django.core.mail import EmailMessage
@ensure_csrf_cookie
def contact(request):
	if request.method == 'POST':
		form = contactforms(request.POST)
		if form.is_valid():
			name = request.POST.get("name", "")
			emailid = request.POST.get("emailid", "")
			enquiry_type = request.POST.get("enquiry_type", "")
			get_enq_type = ''
			to_emails_arr = []
			if enquiry_type == '1':
				get_enq_type = 'Medical Content'
				to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com', 'roma@docmode.com']
			elif enquiry_type == '2':
				get_enq_type = 'Technical'
				to_emails_arr = ['hemant@docmode.com', 'dev@docmode.com', 'paulson@docmode.com']
			elif enquiry_type == '3':
				get_enq_type = 'Certificates'
				to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com', 'roma@docmode.com']
			elif enquiry_type == '4':
				get_enq_type = 'General'
				to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com', 'hemant@docmode.com', 'roma@docmode.com']
			else:
				get_enq_type = 'Sales & Partnership'
				to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com', 'amit.rane@docmode.com', 'shweta.patil@docmode.com']
			phone = request.POST.get("phone", "")
			formmsg = request.POST.get("formmsg", "")
			contact = contactform(name=name, emailid=emailid, phone=phone, inquiry_type=enquiry_type,message=formmsg)
			contact.save()
			# Email the profile with the 
			# contact information
			template = loader.get_template('contact_template.txt')
			context = {
				'contact_name': name,
				'contact_email': emailid,
				'contact_phone': phone,
				'form_content': formmsg,
			}
			content = template.render(context)

			email = EmailMessage(
				"New contact form submission - "+ get_enq_type,
				content,
				"contact@docmode.org" +'',
				to_emails_arr,
				headers = {'Reply-To': emailid }
			)
			email.send()
			messages.success(request, 'Email sent successfully.')
			
			return HttpResponseRedirect(reverse('contact'))
		else:
			context = {
				'errors': form.errors
			}
			return render_to_response('contact.html', context)
	else:
		form = contactforms()
		context = {
			'errors' : "welcome",
			'csrf' : csrf(request)['csrf_token']
		}
		return render_to_response('contact.html', context)
