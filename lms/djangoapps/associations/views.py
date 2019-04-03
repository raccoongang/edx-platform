"""
Associations views functions
"""

import json
import logging
import urllib
import MySQLdb
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.template.context_processors import csrf
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q, Count
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from rest_framework import status
from edxmako.shortcuts import render_to_response, render_to_string, marketing_link
from util.cache import cache, cache_if_anonymous
from lms.djangoapps.reg_form.models import extrafields
from lms.djangoapps.reg_form.views import getuserfullprofile, userdetails
from lms.djangoapps.specialization.models import specializations, categories, cat_sub_category
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys import InvalidKeyError
from student.models import CourseEnrollment
from track.backends.django import TrackingLog
from courseware.courses import (
    get_courses,
    get_course,
    get_course_by_id,
    get_permission_for_course_about,
    get_studio_url,
    get_course_overview_with_access,
    get_course_with_access,
    sort_by_announcement,
    sort_by_start_date,
)

from openedx.core.djangoapps.theming import helpers as theming_helpers

from courseware.models import StudentModule

from student.models import User,UserProfile,CourseAccessRole

#from edx_rest_framework_extensions.authentication import JwtAuthentication
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_oauth.authentication import OAuth2Authentication

from organizations.models import Organization, OrganizationMembers, SponsoringCompany
# from organizations import serializers
from lms.djangoapps.reg_form.models import extrafields
from lms.djangoapps.specialization.views import specializationName
from lms.djangoapps.course_extrainfo.models import course_extrainfo
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

#from lang_pref import LANGUAGE_KEY

import datetime

log = logging.getLogger("edx.courseware")

template_imports = {'urllib': urllib}

# Create your views here.

def index(request):
    from organizations.api import get_organizations

    # org_list = []
    
    org_list = get_organizations()

    sorted_assoc_list = sorted(org_list, key=lambda organizations: organizations['name'])

    context = {
      'organizations' : sorted_assoc_list
    }

    return render_to_response(
      "associations/associations.html",context
    )

def list_categories(request):

    # org_list = []

    category_list = categories.objects.all().order_by('topic_name')
    context = {
      'categories' : category_list
    }
    return render_to_response("associations/categories.html",context)

def list_lectures(request):

    from lms.djangoapps.course_extrainfo.models import course_extrainfo
    # lectures_list = []

    lectures = course_extrainfo.objects.filter(course_type=2).values()
    cid = []
    for courseid in lectures:
      course_id = CourseKey.from_string(courseid['course_id'])
      cid.append(course_id)
    course_data = CourseOverview.objects.all().filter(pk__in=cid).order_by('start')[::-1]
    course_discovery_meanings = getattr(settings, 'COURSE_DISCOVERY_MEANINGS', {})

    context = {
      'lectures_list' : course_data,
      'course_discovery_meanings':course_discovery_meanings
    }
    return render_to_response("associations/lectures.html",context)

def case_study(request):
    from lms.djangoapps.course_extrainfo.models import course_extrainfo
    # case_studies_list = []

    course_cat = course_extrainfo.objects.filter(course_type=3).values()
    cid = []
    for courseid in course_cat:
      course_id = CourseKey.from_string(courseid['course_id'])
      cid.append(course_id)
  
    course_data = CourseOverview.objects.all().filter(pk__in=cid).order_by('start')[::-1]
    course_discovery_meanings = getattr(settings, 'COURSE_DISCOVERY_MEANINGS', {})

    context = {
      'courses' : course_data,
      'course_discovery_meanings':course_discovery_meanings
    }
    return render_to_response("associations/case_studies.html",context)
@login_required
def case_study_form(request):

    context = {
      'user' : request.user
    }
    return render_to_response("associations/case_study_form.html",context)

def stateName(stateId):
    from django.core.exceptions import ObjectDoesNotExist
    statename = ''
    try:
        getDetails = states.objects.get(id=stateId)
        statename = getDetails.rstate
    except ObjectDoesNotExist:
        getDetails = None

    return HttpResponse( statename)

@ensure_csrf_cookie
@cache_if_anonymous()
def association_about(request, organization_id):
	"""
	Display the association's about page.
	"""
	user = request.user
	from organizations.models import Organization, OrganizationCourse, OrganizationSlider, OrganizationMembers
	# from courseware.courses import get_course
	from django.core.exceptions import ObjectDoesNotExist

	try:
		data = Organization.objects.get(short_name=organization_id)
		if data :

			speczs = extrafields.objects.values('specialization').annotate(dcount=Count('specialization'))

			try:
				courses = CourseOverview.objects.all().filter(display_org_with_default=organization_id).order_by('start')[::-1]
			except ObjectDoesNotExist:
				courses = None

			try:
				uc_courses = CourseOverview.objects.all().filter(Q(display_org_with_default=organization_id) & Q(start__gte=datetime.date.today())).order_by('start')
			except ObjectDoesNotExist:
				uc_courses = None

			usertypes = extrafields.objects.values('user_type').annotate(dcount=Count('user_type'))

			orgmembers = OrganizationMembers.objects.values('organization_id').annotate(dcount=Count('organization_id'))

			if request.is_ajax():
				if request.method == 'GET' :
					if user.is_authenticated():
						usr = request.user.id
						usrmail = request.user.email
						gid = request.GET.get('groupid')
						group = Organization.objects.get(id=gid)

						gmember = OrganizationMembers(user_id=usr, organization=group,user_email=usrmail)
						gmember.save()
						return HttpResponse('Joined succesful')

			try:
				slider_images = OrganizationSlider.objects.get(organization_id=data.id)
				sep_images = slider_images.image_s3_urls
			except ObjectDoesNotExist:
				slider_images = None
				sep_images = 'http://www.gettyimages.pt/gi-resources/images/Homepage/Hero/PT/PT_hero_42_153645159.jpg'

			#if slider_images is None:
			#	sep_images = 'http://www.gettyimages.pt/gi-resources/images/Homepage/Hero/PT/PT_hero_42_153645159.jpg'
			#else:
			#	sep_images = slider_images.image_s3_urls

			imgs = sep_images.split(',')
			no_of_slides = len(imgs)
			gusr = request.user.id
			gusr_staff = request.user.is_staff
			try:
				member = OrganizationMembers.objects.get(user_id=gusr,organization_id=data.id)
			except ObjectDoesNotExist:
				member = None

			try:
				member_staff = OrganizationMembers.objects.get(user_id=gusr,organization_id=data.id,is_admin='1')
				#member_staff = OrganizationMembers.objects.get(user_id=gusr,organization_id=data.id)
			except ObjectDoesNotExist:
				member_staff = None

			if member is None:
				grpmember = '0'
			else:
				grpmember = '1'

			if member_staff is None:
				grpstaff = '0'
			else:
				grpstaff = '1'

			context = {
				'association_id': data.id,
				'assoc_name': data.name,
				'assoc_short_name': data.short_name,
				'assoc_description': data.description,
				'assoc_logo': data.logo,
				'courses': courses,
				'uc_lect': uc_courses,
				'speczs' : speczs,
				'orgmembers': orgmembers,
				'usertypes': usertypes,
				'slider_images': imgs,
				'no_of_slides': no_of_slides,
				'csrf' : csrf(request)['csrf_token'],
				'grpmember' : grpmember,
				'gusr_staff' : grpstaff,
			}
		return render_to_response('associations/association_about.html', context)
	except ObjectDoesNotExist:
		notfound = None
		raise Http404 
	

def category(request, category_id):
    """
    Display the subjects page
    """
    # from courseware.courses import get_course
    from django.core.exceptions import ObjectDoesNotExist
    from lms.djangoapps.course_extrainfo.models import course_extrainfo
    try:
      cat = categories.objects.get(topic_short_name=category_id)
    except ObjectDoesNotExist:
      cat = None

    try:
      subcat = cat_sub_category.objects.filter(category_id=cat.id)
    except ObjectDoesNotExist:
      subcat = None

    try:
      course_cat = course_extrainfo.objects.filter(category=cat.id).values()
    except ObjectDoesNotExist:
      course_cat = None

    cid = []
    for courseid in course_cat:
      course_id = CourseKey.from_string(courseid['course_id'])
      cid.append(course_id)
  
    course_data = CourseOverview.objects.all().filter(pk__in=cid).order_by('start')[::-1]

    try:
      course_cat_count = course_extrainfo.objects.filter(category=cat.id).count()
    except ObjectDoesNotExist:
      course_cat_count = "No result found"

    if request.is_ajax():
      if request.method == 'POST' :  
        subcatid = request.POST.get("subcategoryid")
        course_time = request.POST.get("coursetime")
        if subcatid > '0':
          try:
            subcat_courses = course_extrainfo.objects.filter(sub_category__contains=subcatid).values()
          except ObjectDoesNotExist:
            subcat_courses = None

          scid = []
          for courseid in subcat_courses:
            sub_course_id = CourseKey.from_string(courseid['course_id'])
            scid.append(sub_course_id)

          if course_time == '1':
            sub_course_data = CourseOverview.objects.all().filter(Q(pk__in=scid) & Q(start__lte=datetime.date.today())).order_by('start')[::-1]
          elif course_time == '2':
            sub_course_data = CourseOverview.objects.all().filter(Q(pk__in=scid) & Q(start__gte=datetime.date.today())).order_by('start')[::-1]
          else:
            sub_course_data = CourseOverview.objects.all().filter(pk__in=scid).order_by('start')[::-1]

        else:
          if course_time == '1':
            sub_course_data = CourseOverview.objects.all().filter(Q(pk__in=cid) & Q(start__lte=datetime.date.today())).order_by('start')[::-1]
          elif course_time == '2':
            sub_course_data = CourseOverview.objects.all().filter(Q(pk__in=cid) & Q(start__gte=datetime.date.today())).order_by('start')[::-1]
          else:
            sub_course_data = CourseOverview.objects.all().filter(pk__in=cid).order_by('start')[::-1]

        html = render_to_string('associations/courses.html', {'courses': sub_course_data})
        return HttpResponse(html)
    
    context = {
        'category': cat,
        'count' : course_cat_count,
        'courses': course_data,
        'subcat' : subcat
    }

    return render_to_response('associations/category_courses.html', context)

def course_det(courseId):

    course_key = CourseKey.from_string(courseId)

    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

    course_details = CourseOverview.objects.all().filter(id=course_key).values()

    return course_details

def speczName(speczId):
    from django.core.exceptions import ObjectDoesNotExist
    speczname = ''
    try:
        getDetails = specializations.objects.get(id=speczId)
        speczname = getDetails.name
    except ObjectDoesNotExist:
        getDetails = None

    return speczname

def orgName(orgId):
    from django.core.exceptions import ObjectDoesNotExist
    from organizations.models import Organization, OrganizationCourse, OrganizationSlider, OrganizationMembers
    orgname = ''
    try:
        getDetails = Organization.objects.get(id=orgId)
        orgname = getDetails.name
    except ObjectDoesNotExist:
        getDetails = None

    return orgname

def userType(type):
    from django.core.exceptions import ObjectDoesNotExist
    ust = ''
    if type == 'dr':
        ust = 'Doctor'
    elif type == 'u':
        ust = 'User'
    elif type == 'ms':
        ust = 'Medical Student'
    elif type == 'hc':
        ust = 'Healthcare Specialist'

    return ust

@ensure_csrf_cookie
@cache_if_anonymous()
def organization_analytics(request, organization_id):
    """
    Display the association's about page.
    """
    user = request.user
    from organizations.models import Organization, OrganizationCourse, OrganizationSlider, OrganizationMembers
    # from courseware.courses import get_course
    from django.core.exceptions import ObjectDoesNotExist

    data = Organization.objects.get(id=organization_id)

    speczs = extrafields.objects.values('specialization').annotate(dcount=Count('specialization'))
    

    usertypes = extrafields.objects.values('user_type').annotate(dcount=Count('user_type'))
    
    orgmembers = OrganizationMembers.objects.values('organization').annotate(dcount=Count('organization'))

    courses = OrganizationCourse.objects.all().filter(organization_id=organization_id)
    if request.is_ajax():
        if request.method == 'GET':
            if user.is_authenticated():
                cities = extrafields.objects.values('regstate').annotate(dcount=Count('regstate'))
                city_dict = {}
                for city in cities:
                    city_dict[city['regstate']] = city['dcount']
                
                return HttpResponse(json.dumps(city_dict), content_type="application/json")

    try:
        slider_images = OrganizationSlider.objects.filter(organization_id=organization_id)
    except ObjectDoesNotExist:
        slider_images = None

    if slider_images is None:
        sep_images = 'http://www.gettyimages.pt/gi-resources/images/Homepage/Hero/PT/PT_hero_42_153645159.jpg'
    else:
        sep_images = 'http://www.gettyimages.pt/gi-resources/images/Homepage/Hero/PT/PT_hero_42_153645159.jpg'

    imgs = sep_images.split(',')
    no_of_slides = len(imgs)
    gusr = request.user.id
    try:
        member = OrganizationMembers.objects.get(user_id=gusr,organization=organization_id)
    except ObjectDoesNotExist:
        member = None

    if member is None:
        grpmember = '0'
    else:
        grpmember = '1'
    

    context = {
        'association_id': data.id,
        'assoc_name': data.name,
        'assoc_short_name': data.short_name,
        'assoc_description': data.description,
        'courses': courses,
        'slider_images': imgs,
        'no_of_slides': no_of_slides,
        'csrf' : csrf(request)['csrf_token'],
        'grpmember' : grpmember,
    }

    return render_to_response('associations/analytics.html', context)

def get_user_type(sname):
  if sname == 'dr':
    uName = 'Doctor'
  elif sname == 'hc':
    uName = 'Healthcare'
  elif sname == 'u':
    uName = 'Public'
  else:
    uName = 'Medical Student'
  return uName

def getuserlog(cid):
    usercnt = ''
    try:
        usercnt = TrackingLog.objects.filter(event_type__contains=cid).count()
    except ObjectDoesNotExist:
        usercnt = None

    return usercnt

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def custom_analytics(request):

  """Render the custom analytics page for docmode.

  Args:
     request (HttpRequest)

  Returns:
     HttpResponse: 200 if the page was sent successfully
     HttpResponse: 302 if not logged in (redirect to login page)
     HttpResponse: 405 if using an unsupported HTTP method
  Raises:
     Http404: 404 if the specified user is not authorized or does not exist

  Example usage:
     GET /account/profile
  """
  user = request.user
  import datetime

  #if (user.email == 'hemant@docmode.com') or (user.email == 'paulson@docmode.com') or (user.email == 'dev@docmode.com'):
  if user.is_staff:
    from opaque_keys.edx.locations import SlashSeparatedCourseKey
    total_users = User.objects.count()
    users_not_verified = User.objects.filter(is_active=0).count()
    verified_users = User.objects.filter(is_active=1).count()
    total_assoc = Organization.objects.count()
    webinar_count = course_extrainfo.objects.filter(course_type='2').count()
    course_count = course_extrainfo.objects.filter(course_type='1').count()
    usertypes = extrafields.objects.values('user_type').annotate(dcount=Count('user_type')).order_by()
    specQset = extrafields.objects.filter(user_type='dr').exclude(specialization_id__isnull=True).values('specialization_id').annotate(dcount=Count('specialization_id')).order_by()
    hcQset = extrafields.objects.filter(user_type='hc').exclude(hcspecialization_id__isnull=True).values('hcspecialization_id').annotate(dcount=Count('hcspecialization_id')).order_by()
    orgMemQset = OrganizationMembers.objects.values('organization_id').annotate(dcount=Count('user_id')).order_by()
    month_wise_reg = User.objects.values('date_joined').annotate(dcount=Count('date_joined')).order_by()
    course_all = CourseOverview.objects.values('id')
    # course_user_dict = {}
    # for courseid in course_all:
    #     cid = courseid['id'] + '/courseware/'
    #     course_user_dict[cid] = getuserlog(cid)

    #course_viewd_user_cnt = TrackingLog.objects.filter(event_type__contains=course_all).count()
    def specData():
      # sn = []
      # sn.append(['Specialization', 'User Count'])
      # for n in specQset:
      #   sn.append([specializationName(n['specialization_id']),n['dcount']])
      sn = [[specializationName(sn['specialization_id']).encode('ASCII'), sn['dcount']] for sn in specQset]
      return sn

    def userTypes():
      ut = []
      for k in usertypes:
        ut.append(get_user_type(k['user_type']))
      return ut

    def userCount():
      ut = []
      for k in usertypes:
        ut.append(k['dcount'])
      return ut
    
    context = {
      'total_users': total_users,
      'users_not_verified': users_not_verified,
      'verified_users': verified_users,
      'total_assoc': total_assoc,
      'webinar_count': webinar_count,
      'course_count': course_count,
      'usertype_qset': usertypes,
      'spec_data': specData(),
      'spec_qset': specQset,
      'orgMemQset': orgMemQset,
      'hc_qset': hcQset,
      'mwr': month_wise_reg,
      'cal': course_all
    }

    return render_to_response('custom_analytics/custom_analytics.html', context)
  else:
    return HttpResponse('Not Authorized!')

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def custom_analytics_coupons(request):
    # from opaque_keys.edx.locations import SlashSeparatedCourseKey
    # cid = 'mindvision/LMV004/2017_May_LMV004'
    # cid = SlashSeparatedCourseKey.from_deprecated_string(cid)
    # enrollLocationQset = CourseEnrollment.objects.filter(course_id=cid).count()
    # extrafields.objects.filter(user_type='dr').exclude(specialization_id__isnull=True).values('specialization_id').annotate(dcount=Count('specialization_id')).order_by()

    db = MySQLdb.connect("hawthorn-live.c2woekolusus.ap-south-1.rds.amazonaws.com","ecomm001","HjDzeQZlRJcXoRadc8fRnS8HDnlky450mhL","ecommerce")

    # define a cursor object
    cursor = db.cursor()
    sql = "select *,COUNT(*) as count,SUM(num_orders) as total_orders from voucher_voucher group by name order by start_datetime desc"
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()

    context = {
      # 'title': 'Demographics Page',
      # 'locationCount': enrollLocationQset
      'vouchers': results
    }

    return render_to_response('custom_analytics/custom_analytics_coupons.html', context)

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def coupon_details(request, coupon_name):
    
    db = MySQLdb.connect("hawthorn-live.c2woekolusus.ap-south-1.rds.amazonaws.com","ecomm001","HjDzeQZlRJcXoRadc8fRnS8HDnlky450mhL","ecommerce")
    coupon_name = coupon_name
    # define a cursor object
    cursor = db.cursor()
    cursor.execute("SELECT voucher_voucher.id, voucher_voucher.name,voucher_voucher.code,voucher_voucherapplication.date_created,voucher_voucherapplication.order_id,voucher_voucherapplication.user_id,voucher_voucherapplication.voucher_id,ecommerce_user.id,ecommerce_user.email,ecommerce_user.first_name,ecommerce_user.last_name FROM voucher_voucher INNER JOIN voucher_voucherapplication on voucher_voucher.id = voucher_voucherapplication.voucher_id INNER JOIN ecommerce_user on voucher_voucherapplication.user_id = ecommerce_user.id WHERE name = %s",[coupon_name])
    results = cursor.fetchall()
    # voucherid = results[0][0]
    # log.info(u" Order_Voucherid %s", voucherid)
    # order = db.cursor()
    # order.execute("SELECT * from voucher_voucherapplication WHERE voucher_id = %s",[results[0][0]])
    # corder = order.fetchall()
    db.close()

    context = {
        'coupon' : results
    }

    return render_to_response('custom_analytics/custom_analytics_coupon_details.html', context)


def export_coupon_csv(request, coupon_name):
    import csv
    from django.utils.encoding import smart_str
    db = MySQLdb.connect("hawthorn-live.c2woekolusus.ap-south-1.rds.amazonaws.com","ecomm001","HjDzeQZlRJcXoRadc8fRnS8HDnlky450mhL","ecommerce")
    coupon_name = coupon_name
    # define a cursor object
    coupon_cursor = db.cursor()
    coupon_cursor.execute("SELECT voucher_voucher.id, voucher_voucher.name,voucher_voucher.code,voucher_voucherapplication.date_created,voucher_voucherapplication.order_id,voucher_voucherapplication.user_id,voucher_voucherapplication.voucher_id,ecommerce_user.id,ecommerce_user.email,ecommerce_user.first_name,ecommerce_user.last_name FROM voucher_voucher INNER JOIN voucher_voucherapplication on voucher_voucher.id = voucher_voucherapplication.voucher_id INNER JOIN ecommerce_user on voucher_voucherapplication.user_id = ecommerce_user.id WHERE voucher_voucher.name = %s",[coupon_name])
    coupon_results = coupon_cursor.fetchall()
    db.close()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename='+coupon_name+'_'+str(datetime.date.today())+'.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    #log.info(u" coupondata %s", coupon_results)
    user = request.user

    if (user.is_staff):
        writer.writerow([
            smart_str(u"Coupon Code"),
            smart_str(u"Emailid"),
            smart_str(u"Name"),
            smart_str(u"Phone"),
            smart_str(u"State"),
            smart_str(u"City"),
            smart_str(u"Date"),
        ])
        response['Content-Disposition'] = 'attachment; filename='+coupon_name+'_'+str(datetime.date.today())+'.csv'
        for coupon in coupon_results:
            cuser = User.objects.filter(email=coupon[8]).values('id')
            user_phone = userdetails(cuser)
            user_profile = getuserfullprofile(cuser)
            writer.writerow([
                smart_str(coupon[2].encode('ASCII')),
                smart_str(coupon[8]),
                smart_str(user_profile.name),
                smart_str(user_phone.phone),
                smart_str(user_phone.rstate),
                smart_str(user_phone.rcity),
                smart_str(coupon[3]),
            ])

    return response
export_coupon_csv.short_description = u"Export Coupon CSV"

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def custom_analytics_viewership(request):

    def getState(userId):
        statename = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            statename = getDetails.rstate
        except ObjectDoesNotExist:
            getDetails = None

        return statename

    def getCity(userId):
        cityname = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            cityname = getDetails.rcity
        except ObjectDoesNotExist:
            getDetails = None

        return cityname

    def getViewerName(userId):
        vName = ''
        try:
            getDetails = UserProfile.objects.get(user_id=userId)
            vName = getDetails.name
        except ObjectDoesNotExist:
            getDetails = None

        return vName

    def getViewerEmail(userId):
        vEmail = ''
        try:
            getDetails = User.objects.get(id=userId)
            vEmail = getDetails.email
        except ObjectDoesNotExist:
            getDetails = None

        return vEmail

    if request.is_ajax():
        if 'courseid' in request.GET :
            from opaque_keys.edx.locations import SlashSeparatedCourseKey
            cid = request.GET.get("courseid")
            cid = SlashSeparatedCourseKey.from_deprecated_string(cid)
            count = StudentModule.objects.filter(course_id=cid,module_type='video').count()
            crows = StudentModule.objects.filter(Q(module_type='video') & Q(course_id=cid)).values('state','student_id','course_id')
            rows = [[s['state'].encode('ASCII'), getViewerName(s['student_id']).encode('ASCII'), getViewerEmail(s['student_id']), getState(s['student_id']), getCity(s['student_id']), s['course_id']] for s in crows]

            user_dict = {}
            for row in crows:
                user_dict['name'] = getViewerName(row['student_id']).encode('ASCII')
                user_dict['state'] = getState(row['student_id']).encode('ASCII')
                user_dict['city'] = getCity(row['student_id']).encode('ASCII')
                user_dict['email'] = getViewerEmail(row['student_id']).encode('ASCII')
                user_dict['viewed'] = row['state'].encode('ASCII')

            return HttpResponse(json.dumps(user_dict), content_type="application/json")
        else:
            data = request.GET
            courseid = data.get("term")
            if courseid:
                courses = CourseOverview.objects.filter(id__icontains= courseid)
            else:
                courses = CourseOverview.objects.all()
            results = []
            for course in courses:
                course_json = {}
                course_json['id'] = course.display_number_with_default
                course_json['label'] = course.display_name
                course_json['value'] = course.display_name
                results.append(course_json)

            data = json.dumps(results)
            mimetype = 'application/json'
            return HttpResponse(data, mimetype)

    from opaque_keys.edx.locations import SlashSeparatedCourseKey

    course_id = SlashSeparatedCourseKey.from_deprecated_string('docmode/dm002/2017_dm002')


    viewersQset = StudentModule.objects.filter(Q(module_type='video')).values('state','student_id','course_id')
    rows = [[s['state'].encode('ASCII'), getViewerName(s['student_id']).encode('ASCII'), getViewerEmail(s['student_id']), getState(s['student_id']), getCity(s['student_id']), s['course_id']] for s in viewersQset]
    courses = CourseOverview.objects.all()
    context = {
        'title': 'Viewership Page',
        'qset': viewersQset,
        'rows': rows,
        'courses': courses
    }

    return render_to_response('custom_analytics/custom_analytics_viewership.html', context)

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def association_dashboard(request, org_sname):
    
    from organizations.models import OrganizationCourse, OrganizationMembers
    gusr = request.user.id
    data = Organization.objects.get(short_name=org_sname)
    try:
        member_staff = OrganizationMembers.objects.get(user_id=gusr,organization_id=data.id,is_admin='1')
        if member_staff.course_ids != '':
          admin_courseids = member_staff.course_ids.split(",")
          cid = []
          for courseid in admin_courseids:          
            course_id = CourseKey.from_string(courseid)
            cid.append(course_id)
        else:
          cid = "None"
    except ObjectDoesNotExist:
        member_staff = None
        cid = None

    if member_staff is None:
        grpstaff = '0'
    else:
        grpstaff = '1'

    try:
        courses = CourseOverview.objects.all().filter(Q(display_org_with_default=org_sname) & Q(catalog_visibility='both')).order_by('-start')
    except ObjectDoesNotExist:
        courses = None
    total_members = OrganizationMembers.objects.filter(organization_id=data.id).count()
    # webinar_count = course_extrainfo.objects.filter(course_type='1', display_org_with_default=org_sname).count()
    webinar_count = OrganizationCourse.objects.filter(organization_id=data.id).count()
    context = {
        'association_id': data.id,
        'assoc_name': data.name,
        'assoc_short_name': data.short_name,
        'assoc_logo': data.logo,
        'courses': courses,
        'total_members': total_members,
        'total_webinars': webinar_count,
        'grp_admin': grpstaff,
        'admin_courses' : cid
    }

    return render_to_response('associations/association_dashboard.html', context)

def course_usercount(userId):
    try:
        getDetails = CourseEnrollment.objects.filter(course_id=userId).count()
    except ObjectDoesNotExist:
        getDetails = "No data"

    return getDetails

def course_viewercount(userId):
    try:
        getDetails = StudentModule.objects.filter(course_id=userId,module_type='video').count()
    except ObjectDoesNotExist:
        getDetails = "No data"
    return getDetails

def organizationName(orgId):
    orgname = ''
    try:
        getDetails = Organization.objects.get(id=orgId)
	orgname = getDetails.name
    except ObjectDoesNotExist:
	getDetails = None

    return orgname

@login_required
@ensure_csrf_cookie
@require_http_methods(['GET'])
def association_course_analytics(request,course_id):

    from organizations.models import OrganizationCourse, OrganizationMembers
    gusr = request.user.id
    org_course = OrganizationCourse.objects.get(course_id=course_id)
    try:
        member_staff = OrganizationMembers.objects.get(user_id=gusr,organization_id=org_course.organization_id,is_admin='1')
        #member_staff = OrganizationMembers.objects.get(user_id=gusr,organization_id=data.id)
    except ObjectDoesNotExist:
        member_staff = None

    if member_staff is None:
        grpstaff = '0'
    else:
        grpstaff = '1'

    def getState(userId):
        statename = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            statename = getDetails.rstate
        except ObjectDoesNotExist:
            getDetails = None

        return statename

    def getCity(userId):
        cityname = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            cityname = getDetails.rcity
        except ObjectDoesNotExist:
            getDetails = None

        return cityname

    def getViewerName(userId):
        vName = ''
        try:
            getDetails = UserProfile.objects.get(user_id=userId)
            vName = getDetails.name
        except ObjectDoesNotExist:
            getDetails = None

        return vName

    def getViewerEmail(userId):
        vEmail = ''
        try:
            getDetails = User.objects.get(id=userId)
            vEmail = getDetails.email
        except ObjectDoesNotExist:
            getDetails = None

        return vEmail

    if request.is_ajax():
        if 'courseid' in request.GET :
            from opaque_keys.edx.locations import SlashSeparatedCourseKey
            cid = request.GET.get("courseid")
            cid = SlashSeparatedCourseKey.from_deprecated_string(cid)
            count = StudentModule.objects.filter(course_id=cid,module_type='video').count()
            crows = CourseEnrollment.objects.filter(course_id=cid)
            results = []
            for row in crows:
                user = {}
                user['name'] = getViewerName(row.user_id).encode('ASCII')
                user['state'] = getState(row.user_id).encode('ASCII')
                user['city'] = getCity(row.user_id).encode('ASCII')
                user['email'] = getViewerEmail(row.user_id).encode('ASCII')
                results.append(user)
            data = results
            return HttpResponse(json.dumps(data), content_type="application/json")

    from opaque_keys.edx.locations import SlashSeparatedCourseKey
    cid = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    try:
        course = CourseOverview.objects.get(id=cid)
    except ObjectDoesNotExist:
        course = None

    try:
        enrolleduser = CourseEnrollment.objects.filter(course_id=cid, is_active=1).count()
    except ObjectDoesNotExist:
        enrolleduser = "No data"

    try:
        viewers = StudentModule.objects.filter(course_id=cid,module_type='video').count()
    except ObjectDoesNotExist:
        viewers = "No data"
    data = Organization.objects.get(short_name=course.display_org_with_default)

    cenrolls = CourseEnrollment.objects.filter(course_id=cid).values('user_id')
    specQset = extrafields.objects.filter(user__id__in=cenrolls).exclude(rpincode=0).values('rstate').annotate(dcount=Count('rstate'))
    enrolleduserspecz = extrafields.objects.filter(user__id__in=cenrolls).exclude(specialization_id__isnull=True).values('specialization_id').annotate(dcount=Count('specialization_id'))
    
    vieweduser = StudentModule.objects.filter(course_id=cid,module_type='video').values('student_id')
    courseviewers = extrafields.objects.filter(user__id__in=vieweduser).exclude(rpincode=0).values('rstate').annotate(dcount=Count('rstate'))
    viewerspecz = extrafields.objects.filter(user__id__in=vieweduser).exclude(specialization_id__isnull=True).values('specialization_id').annotate(dcount=Count('specialization_id'))
    context = {
        'association_id': data.id,
        'assoc_name': data.name,
        'assoc_short_name': data.short_name,
        'assoc_logo': data.logo,
        'courses': course,
        'total_enrolled': enrolleduser,
        'total_viewers': viewers,
        'enrolldata': specQset,
        'viewers' : courseviewers,
        'enrolleduserspecz' : enrolleduserspecz,
        'viewerspecz' : viewerspecz,
        'org_admin' : grpstaff
    }

    return render_to_response('associations/association_course_analytics.html', context)

def export_csv(request, course_id, datatype):
    import csv
    from django.utils.encoding import smart_str

    from opaque_keys.edx.locations import SlashSeparatedCourseKey
    cid = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=users.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)

    def getState(userId):
        statename = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            if getDetails.rstate != ' ':
                statename = getDetails.rstate
            else:
                statename = 'N/A'
        except ObjectDoesNotExist:
            getDetails = None

        return statename

    def getCity(userId):
        cityname = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            if getDetails.rcity != ' ':
                cityname = getDetails.rcity
            else:
                cityname = 'N/A'
        except ObjectDoesNotExist:
            getDetails = None

        return cityname

    def getspecialization(userId):
        from lms.djangoapps.specialization.views import specializationName
        speczname = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            specname = specializationName(getDetails.specialization_id)
            if specname != ' ':
                speczname = specname
            else:
                speczname = 'N/A'
        except ObjectDoesNotExist:
            speczname = 'N/A'

        return speczname

    def getPincode(userId):
        pincode = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            pincode = getDetails.rpincode
        except ObjectDoesNotExist:
            getDetails = None
        return pincode

    def getmci(userId):
        mci = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId,user_type='dr')
            mci = getDetails.reg_num
        except ObjectDoesNotExist:
            mci = 'N/A'
        return mci

    def getusertype(userId):
        u_type = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            utype = getDetails.user_type
            if utype == 'dr' :
                u_type = 'Doctor'
            elif utype == 'hc':
                u_type == 'Healthcare Specialists'
            elif utype == 'ms' :
                u_type = 'Medical Student'
            elif utype == 'u':
                u_type = 'User'
        except ObjectDoesNotExist:
            u_type = 'N/A'
        return u_type

    def getphone(userId):
        phone = ''
        try:
            getDetails = extrafields.objects.get(user_id=userId)
            phone = getDetails.phone
        except ObjectDoesNotExist:
            phone = 'N/A'
        return phone

    def getViewerName(userId):
        vName = ''
        try:
            getDetails = UserProfile.objects.get(user_id=userId)
            vName = getDetails.name
        except ObjectDoesNotExist:
            getDetails = None

        return vName

    def getemail(userId):
        vEmail = ''
        try:
            getDetails = User.objects.get(id=userId)
            vEmail = getDetails.email
        except ObjectDoesNotExist:
            getDetails = None

        return vEmail

    # def getLastname(userId):
    #     lname = ''
    #     try:
    #         getDetails = UserProfile.objects.get(user_id=userId)
    #         lname = getDetails.lname
    #     except ObjectDoesNotExist:
    #         lname = 'N/A'
    #     return lname

    course_id = str(cid)
    course_number = course_id.split('+')
    user = request.user

    if (user.is_staff):
        writer.writerow([
            smart_str(u"Name"),
            # smart_str(u"Last Name"),
            smart_str(u"Emailid"),
            smart_str(u"Mobile"),
            smart_str(u"Type"),
            smart_str(u"MCI"),
            smart_str(u"Specialization"),
            smart_str(u"State"),
            smart_str(u"City"),
            smart_str(u"Pincode"),
            smart_str(u"Date"),
            smart_str(u"Video Watch time"),
        ])
        if datatype == 'enrolled' :
            response['Content-Disposition'] = 'attachment; filename='+ str(course_number[1]) +'_enrolledusers.csv'
            crows = CourseEnrollment.objects.filter(course_id=cid)
            for row in crows:
                writer.writerow([
                    smart_str(getViewerName(row.user_id)),
                    # smart_str(getLastname(row.user_id)),
                    smart_str(getemail(row.user_id).encode('ASCII')),
                    smart_str(getphone(row.user_id).encode('ASCII')),
                    smart_str(getusertype(row.user_id).encode('ASCII')),
                    smart_str(getmci(row.user_id).encode('ASCII')),
                    smart_str(getspecialization(row.user_id)),
                    smart_str(getState(row.user_id)),
                    smart_str(getCity(row.user_id)),
                    smart_str(getPincode(row.user_id).encode('ASCII')),
                    smart_str(row.created),
                    smart_str('N/A'),
                ])
        elif datatype == 'viewers' :
            response['Content-Disposition'] = 'attachment; filename='+ str(course_number[1]) +'_viewers.csv'
            vrows = StudentModule.objects.filter(course_id=cid,module_type='video')
            for vrow in vrows:
                writer.writerow([
                    smart_str(getViewerName(vrow.student_id)),
                    # smart_str(getLastname(vrow.student_id).encode('ASCII')),
                    smart_str(getemail(vrow.student_id).encode('ASCII')),
                    smart_str(getphone(vrow.student_id).encode('ASCII')),
                    smart_str(getusertype(vrow.student_id).encode('ASCII')),
                    smart_str(getmci(vrow.student_id).encode('ASCII')),
                    smart_str(getspecialization(vrow.student_id)),
                    smart_str(getState(vrow.student_id)),
                    smart_str(getCity(vrow.student_id)),
                    smart_str(getPincode(vrow.student_id)),
                    smart_str(vrow.created),
                    smart_str(vrow.state),
                ])
    else:
        writer.writerow([
            smart_str(u"Name"),
            # smart_str(u"Last Name"),
            smart_str(u"Type"),
            smart_str(u"MCI"),
            smart_str(u"Specialization"),
            smart_str(u"State"),
            smart_str(u"City"),
            smart_str(u"Pincode"),
            smart_str(u"Date"),
        ])
        if datatype == 'enrolled' :
            response['Content-Disposition'] = 'attachment; filename='+ str(course_number[1]) +'_enrolledusers.csv'
            crows = CourseEnrollment.objects.filter(course_id=cid)
            for row in crows:
                writer.writerow([
                    smart_str(getViewerName(row.user_id).encode('ASCII')),
                    # smart_str(getLastname(row.user_id).encode('ASCII')),
                    smart_str(getusertype(row.user_id).encode('ASCII')),
                    smart_str(getmci(row.user_id).encode('ASCII')),
                    smart_str(getspecialization(row.user_id).encode('ASCII')),
                    smart_str(getState(row.user_id)),
                    smart_str(getCity(row.user_id)),
                    smart_str(getPincode(row.user_id).encode('ASCII')),
                    smart_str(row.created),
                ])
        elif datatype == 'viewers' :
            response['Content-Disposition'] = 'attachment; filename='+ str(course_number[1]) +'_viewers.csv'
            vrows = StudentModule.objects.filter(course_id=cid,module_type='video')
            for vrow in vrows:
                writer.writerow([
                    smart_str(getViewerName(vrow.student_id).encode('ASCII')),
                    # smart_str(getLastname(vrow.student_id).encode('ASCII')),
                    smart_str(getusertype(vrow.student_id).encode('ASCII')),
                    smart_str(getmci(vrow.student_id).encode('ASCII')),
                    smart_str(getspecialization(vrow.student_id).encode('ASCII')),
                    smart_str(getState(vrow.student_id)),
                    smart_str(getCity(vrow.student_id)),
                    smart_str(getPincode(vrow.student_id).encode('ASCII')),
                    smart_str(vrow.created),
                ])

    return response
export_csv.short_description = u"Export CSV"

def autojoin_org(userid, course_id, email):

    from organizations.models import OrganizationMembers
    from organizations.models import OrganizationCourse

    org_id = OrganizationCourse.objects.get(course_id=course_id)

    gmember = OrganizationMembers(user_id=userid, organization_id=org_id.organization_id, user_email=email)
    gmember.save()

def assoc_join(userid, org_id, email):
    from organizations.models import OrganizationMembers

    data = Organization.objects.get(short_name=org_id)
    gmember = OrganizationMembers(user_id=userid, organization_id=data.id, user_email=email)
    gmember.save()


def check_domain_in_usermail(sponsoring_companyname="lupin"):
    from organizations.models import SponsoringCompany
    try:
        sname = SponsoringCompany.objects.filter(name=sponsoring_companyname)
        found = 1
    except ObjectDoesNotExist:
        found = 0
    return found
