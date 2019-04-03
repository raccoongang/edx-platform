import logging
import json
import urlparse
import os
import boto
import boto.s3
import sys
from boto.s3.key import Key
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,HttpResponseRedirect
)
from django.core.files.storage import FileSystemStorage
from django.template import RequestContext, Template, loader, context
from django.shortcuts import redirect
from django.http import HttpRequest
from django_countries import countries
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import ugettext as _

from django.views.decorators.http import require_http_methods
from django.core.context_processors import csrf
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
from lms.djangoapps.case_study.models import case_study_abstracts
from lms.djangoapps.case_study.forms import case_study_abstracts_form

from student.helpers import get_next_url_for_login_page
import third_party_auth
from third_party_auth import pipeline
from third_party_auth.decorators import xframe_allow_whitelisted
from util.bad_request_rate_limiter import BadRequestRateLimiter

from openedx.core.djangoapps.user_api.accounts.api import request_password_change
from openedx.core.djangoapps.user_api.errors import UserNotFound
from django.core.mail import EmailMessage
AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)

@login_required
@ensure_csrf_cookie
def cs_addnew(request):
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

    if request.method == 'POST':
        user = request.user.id
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        upload_file = request.FILES['my_file']
        user_type = request.POST.get("user_type", "")
        case_study_type = request.POST.get("case_study_type", "")

        # AWS Storing start
        username = request.user.username
        bucket_dir = BUCKET_NAME +'/'+ username +'-'+ case_study_type + '-one/'
        #bucket_dir = BUCKET_NAME
        file_name = upload_file.name
        ext = os.path.splitext(upload_file.name)[1]
        valid_extensions = ['.pdf','.doc','.docx']
        if not ext in valid_extensions:
            raise ValidationError(u'File not supported!')

        # log.info('extension %s', ext)
        s3_connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        log.info('xxxxx %s', bucket_dir)

        # bucket = s3_connection.get_bucket(bucket_dir)
        # key = boto.s3.key.Key(bucket, file_name)
        # with open(file_name) as f:
        #     key.send_file(f)

        bucket = conn.create_bucket(bucket_name+'/cs_uploads',
            location=boto.s3.connection.Location.DEFAULT)
        k = Key(BUCKET_NAME)
        k.set_contents_from_filename(upload_file)
        
        case_study = case_study_abstracts(user_id=user,title=title,description=description, user_type=user_type, case_study_type=case_study_type)
        case_study.save()

        msg = "Case study uploaded sucessfullly"
        # else:
        #     msg = "File size should not exceed 25Mb"
        context = {
            'errors': msg
        }
        return render_to_response('case_study/case_study_add.html', context)
    else:
        form = case_study_abstracts_form()
        context = {
            'errors' : "welcome",
            'csrf' : csrf(request)['csrf_token']
        }
        return render_to_response('case_study/case_study_add.html', context)

def cs_update(request):
    form = case_study_abstracts_form()
    return render(request, 'case_study/case_study_edit.html', {'form': form})

def csy_dashboard(request):
    form = case_study_abstracts_form()
    return render(request, 'case_study/csy_competition_dashboard.html', {'form': form})

def csy_about(request):
    abstract = "Testing the case study competition page"
    context= {
        'cs_competition' : abstract
    }
    return render_to_response('case_study/csy_competition_about.html',context)