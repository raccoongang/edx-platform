import logging
import boto
import boto.s3
import sys
from boto.s3.key import Key
import boto.s3.connection
from datetime import date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,HttpResponseRedirect
)
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from lms.djangoapps.case_study.models import case_study_abstracts
from lms.djangoapps.case_study.forms import case_study_abstracts_form
from edxmako.shortcuts import render_to_response
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist

AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

@login_required
@ensure_csrf_cookie
def cs_addnew(request):
    if request.method == 'POST':
        user = request.user.id
        #upload_file = request.FILES['my_file']
        #bucket_name = AWS_ACCESS_KEY_ID.lower() + '-dump'
        username = request.user.username
        case_study_type = request.POST.get("case_study_type", "")
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        user_type = request.POST.get("user_type", "")
        case_study_type = request.POST.get("case_study_type", "")

        bucket_name = BUCKET_NAME +'/'+ username +'-'+ case_study_type + '-one/'
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                AWS_SECRET_ACCESS_KEY)

        #bucket = conn.create_bucket(bucket_name,location=boto.s3.connection.Location.DEFAULT)
        bucket = conn.get_bucket(BUCKET_NAME)
        #bucket = BUCKET_NAME
        imagedate = date.today()
        imagedate = imagedate.strftime('%d_%m_%Y')
        #testfile = upload_file.name
        imageurl = ''
        if request.FILES:
            for myfile in request.FILES.getlist('my_file[]'):
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                log.info('uploaded_file_url %s', uploaded_file_url)

                k = Key(bucket)
                k.key = username+'_new_'+imagedate+'_'+myfile.name
                k.set_contents_from_filename(settings.MEDIA_ROOT+'/'+myfile.name)
                k.make_public()
                imageurl += 'https://s3-ap-southeast-1.amazonaws.com/docmode-org-uploads/'+username+'_new_'+imagedate+'_'+myfile.name+','
        author_name = ','.join(map(str, request.POST.getlist('author_names[]')))
        author_email = ','.join(map(str, request.POST.getlist('author_emails[]')))
        author_affiliation = ','.join(map(str, request.POST.getlist('author_affiliations[]')))
        tos = request.POST.get("tos", "")
        case_study = case_study_abstracts(user_id=user,title=title,description=description, user_type=user_type,
        case_study_type=case_study_type,uploaded_file=imageurl,author_name=author_name,
            author_email=author_email,author_affiliation=author_affiliation,tos=tos)
        case_study.save()

        msg ="Case Study uploaded successfully."
        context = {
        'errors': msg
        }
        return render_to_response('case_study/case_study_add.html', context)
    else:
        form = case_study_abstracts_form()
        context = {
        'errors' : "",
        'csrf' : csrf(request)['csrf_token']
        }
        return render_to_response('case_study/case_study_add.html', context)

@login_required
@ensure_csrf_cookie
def cs_update(request,caseid):
    userid = request.user.id
    username = request.user.username
    try:
        case_dat1 = case_study_abstracts.objects.get(id=caseid)   
        if request.method == 'POST':
            user = userid
            case_dat1.title = request.POST.get("title", "")
            case_dat1.description = request.POST.get("description", "")
            case_dat1.user_type = request.POST.get("user_type", "")
            case_dat1.case_study_type = request.POST.get("case_study_type", "")
            author_name = ','.join(map(str, request.POST.getlist('author_names[]')))
            author_email = ','.join(map(str, request.POST.getlist('author_emails[]')))
            author_affiliation = ','.join(map(str, request.POST.getlist('author_affiliations[]')))
            case_dat1.author_name = author_name
            case_dat1.author_email = author_email
            case_dat1.author_affiliation = author_affiliation
            case_dat1.tos = request.POST.get("tos", "")
            if request.FILES:
                upload_file = request.FILES['my_file[]']            
                conn = boto.connect_s3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
                #bucket = conn.create_bucket(bucket_name,location=boto.s3.connection.Location.DEFAULT)
                bucket = conn.get_bucket(BUCKET_NAME)
                #bucket = BUCKET_NAME
                imagedate = date.today()
                imagedate = imagedate.strftime('%d_%m_%Y')
                #testfile = upload_file.name
                db_imageurls = case_dat1.uploaded_file
                db_splitted_imageurls = case_dat1.uploaded_file.split(',')
                
                for myfile in request.FILES.getlist('my_file[]'):
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    uploaded_file_url = fs.url(filename)
                    log.info('uploaded_file_url %s', uploaded_file_url)

                    k = Key(bucket)
                    k.key = username+'_new_'+imagedate+'_'+myfile.name
                    k.set_contents_from_filename(settings.MEDIA_ROOT+'/'+myfile.name)
                    k.make_public()
                    newimageurl = 'https://s3-ap-southeast-1.amazonaws.com/docmode-org-uploads/'+username+'_new_'+imagedate+'_'+myfile.name
                    if newimageurl not in db_splitted_imageurls:
                        db_imageurls += ','+newimageurl
                case_dat1.uploaded_file = db_imageurls          
            msg = "Case study updated sucessfullly"
            case_dat1.save()
            case_dat2 = case_study_abstracts.objects.get(id=caseid)
            context = {
                'case_data' : case_dat2,
                'errors': msg
            }
            return render_to_response('case_study/case_study_edit.html', context)
        else:
            case_data = case_study_abstracts.objects.get(id=caseid)
            # log.info('file details %s', case_data)
            context = {
            	'case_data' : case_data,
                'errors' : "Update Case study",
                'csrf' : csrf(request)['csrf_token']
            }
        return render_to_response('case_study/case_study_edit.html', context)
    except ObjectDoesNotExist :
        context = {
            'errors' : "Please submit your case study here.",
            'csrf' : csrf(request)['csrf_token']
        }
        return render_to_response('case_study/case_study_add.html', context)

@login_required
def csy_dashboard(request):
    userid = request.user.id
    case_data = case_study_abstracts.objects.filter(user_id=userid)
    context = {
        'case_data' : case_data,
        'errors' : "welcome",
        'csrf' : csrf(request)['csrf_token']
    }
    return render_to_response('case_study/csy_competition_dashboard.html', context)

def csy_about(request):
	abstract = "Testing the case study competition page"
	context= {
		'cs_competition' : abstract
	}
	return render_to_response('case_study/csy_competition_about.html',context)

@login_required
def csy_admin_dashboard(request):
    userid = request.user.id
    case_data = case_study_abstracts.objects.all()
    context = {
        'case_data' : case_data
    }
    return render_to_response('case_study/csy_competition_admin.html', context)