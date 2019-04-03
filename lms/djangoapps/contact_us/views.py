import logging
import json
import urlparse
import re 

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,HttpResponseRedirect
)
from django.template import RequestContext, Template, loader, context
from django.shortcuts import redirect
from django.http import HttpRequest
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import ugettext as _

from django.views.decorators.http import require_http_methods
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from edxmako.shortcuts import render_to_response

from student.models import UserProfile

from lms.djangoapps.contact_us.models import contact_us_form
from lms.djangoapps.contact_us.forms import contact_us_frm
from django.core.mail import EmailMessage
from zerobounce import ZeroBounceAPI

AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)

@ensure_csrf_cookie
def contact_us(request):
	if request.method == 'POST':
		# x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		# if x_forwarded_for:
		# 	ip = x_forwarded_for.split(',')[0]
		# else:
		# 	ip = request.META.get('REMOTE_ADDR')
		form = contact_us_frm(request.POST)
		if form.is_valid():
			form_msg = Find(request.POST.get("message", ""))
			if not form_msg:
				zba = ZeroBounceAPI('af8e53a08b7a4a9ab3cc98584fd3a734')			
				name = request.POST.get("name", "")
				emailid = request.POST.get("emailid", "")
				zerobounce_resp = zba.validate(emailid)
				log.info('zerobounce %s',form_msg)
				if zerobounce_resp.status == 'Valid' :
					log.info('zerobounce %s',zerobounce_resp.status)
					enquiry_type = request.POST.get("inquiry_type", "")
					form_msg = request.POST.get("message", "")
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
						to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com','roma@docmode.com']
					else:
						get_enq_type = 'Sales & Partnership'
						to_emails_arr = ['hans@docmode.com', 'paulson@docmode.com', 'romario.rane@docmode.com', 'shweta.patil@docmode.com']
					
					phone = request.POST.get("phone", "")
					contact = contact_us_form.objects.create(name=name, emailid=emailid, phone=phone, inquiry_type=enquiry_type,message=form_msg)
					
					# Email the profile with the 
					# contact information
					template = loader.get_template('contact_template.txt')
					context = {
						'contact_name': name,
						'contact_email': emailid,
						'contact_phone': phone,
						'form_content': form_msg,
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
				else:
					messages.success(request, 'Ivalid emailid.')
			else:
				messages.success(request, 'Urls not allowed in message box.')
			return HttpResponseRedirect(reverse('contact'))
		else:
			context = {
				'errors': form.errors
			}
			return render_to_response('static_template/contact.html', context)
	else:
		form = contact_us_form()
		context = {
			'errors' : "welcome",
			'csrf' : csrf(request)['csrf_token']
		}
		return render_to_response('static_template/contact.html', context)


def Find(string): 
    # findall() has been used  
    # with valid conditions for urls in string 
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string) 
    return url 