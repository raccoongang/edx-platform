""" Views for a student's profile information. """
import json
from badges.utils import badges_enabled
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import Http404,HttpRequest, HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django_countries import countries
from edxmako.shortcuts import marketing_link
from openedx.core.djangoapps.credentials.utils import get_credentials_records_url
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.api import get_account_settings
from openedx.core.djangoapps.user_api.errors import UserNotAuthorized, UserNotFound
from openedx.core.djangoapps.user_api.preferences.api import get_user_preferences
from openedx.core.djangoapps.util.user_messages import PageLevelMessages
from openedx.core.djangolib.markup import HTML, Text
from student.models import User
# added by docmode to get user enrolled courses
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from lms.djangoapps.reg_form.models import extrafields

from .. import SHOW_PROFILE_MESSAGE

from learner_achievements import LearnerAchievementsFragmentView


@login_required
@require_http_methods(['GET'])
def learner_profile(request, username):
    """Render the profile page for the specified username.

    Args:
        request (HttpRequest)
        username (str): username of user whose profile is requested.

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
    usr = request.user.id
    """ User Account update function starts"""
    if request.is_ajax():
        if request.method == 'GET' :
            vfields = request.GET
            for key in vfields:
                vfield = key   
            columname = vfield   
            fieldvalue = vfields[key]
            gmember = extrafields.objects.filter(user_id=usr).update(**{ columname: fieldvalue })
            msg = ' Updated succesfully'
            return HttpResponse(msg)
    try:
        context = learner_profile_context(request, username, request.user.is_staff)
        # TODO: LEARNER-2554: 09/2017: Remove message and cookie logic when we no longer want this message
        message_viewed = False
        if (context['own_profile'] and
                SHOW_PROFILE_MESSAGE.is_enabled() and
                request.COOKIES.get('profile-message-viewed', '') != 'True'):
            message_text = Text(_(
                'Welcome to the new learner profile page. Your full profile now displays more '
                'information to other learners. You can instead choose to display a limited '
                'profile. {learn_more_link_start}Learn more{learn_more_link_end}'
            )).format(
                learn_more_link_start=HTML(
                    '<a href="https://edx.readthedocs.io/projects/open-edx-learner-guide/en/'
                    'latest/SFD_dashboard_profile_SectionHead.html#adding-profile-information">'
                ),
                learn_more_link_end=HTML('</a>')
            )
            PageLevelMessages.register_info_message(request, message_text, dismissable=True)
            message_viewed = True
        response = render_to_response(
            'learner_profile/learner_profile.html',
            context
        )

        if message_viewed:
            response.set_cookie('profile-message-viewed', 'True')
        return response
    except (UserNotAuthorized, UserNotFound, ObjectDoesNotExist):
        raise Http404
    

def learner_profile_context(request, profile_username, user_is_staff):
    """Context for the learner profile page.

    Args:
        logged_in_user (object): Logged In user.
        profile_username (str): username of user whose profile is requested.
        user_is_staff (bool): Logged In user has staff access.
        build_absolute_uri_func ():

    Returns:
        dict

    Raises:
        ObjectDoesNotExist: the specified profile_username does not exist.
    """
    profile_user = User.objects.get(username=profile_username)
    logged_in_user = request.user

    own_profile = (logged_in_user.username == profile_username)

    account_settings_data = get_account_settings(request, [profile_username])[0]

    preferences_data = get_user_preferences(profile_user, profile_username)

    achievements_fragment = LearnerAchievementsFragmentView().render_to_fragment(
        request,
        username=profile_user.username,
        own_profile=own_profile,
    )
    user_enrolled_courses = CourseEnrollment.objects.filter(user_id=logged_in_user.id,is_active=1)
    cid = []
    for courseid in user_enrolled_courses:
      course_id = courseid.course_id
      cid.append(course_id)
  
    course_data = CourseOverview.objects.all().filter(pk__in=cid).order_by('start')[::-1]
    user_extra_info = extrafields.objects.get(user_id=logged_in_user.id)
    context = {
        'own_profile': own_profile,
        'achievements_fragment': achievements_fragment,
        'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
        'data': {
            'profile_user_id': profile_user.id,
            'default_public_account_fields': settings.ACCOUNT_VISIBILITY_CONFIGURATION['public_fields'],
            'default_visibility': settings.ACCOUNT_VISIBILITY_CONFIGURATION['default_visibility'],
            'accounts_api_url': reverse("accounts_api", kwargs={'username': profile_username}),
            'preferences_api_url': reverse('preferences_api', kwargs={'username': profile_username}),
            'preferences_data': preferences_data,
            'account_settings_data': account_settings_data,
            'profile_image_upload_url': reverse('profile_image_upload', kwargs={'username': profile_username}),
            'profile_image_remove_url': reverse('profile_image_remove', kwargs={'username': profile_username}),
            'profile_image_max_bytes': settings.PROFILE_IMAGE_MAX_BYTES,
            'profile_image_min_bytes': settings.PROFILE_IMAGE_MIN_BYTES,
            'account_settings_page_url': reverse('account_settings'),
            'has_preferences_access': (logged_in_user.username == profile_username or user_is_staff),
            'own_profile': own_profile,
            'country_options': list(countries),
            'find_courses_url': marketing_link('COURSES'),
            'language_options': settings.ALL_LANGUAGES,
            'badges_logo': staticfiles_storage.url('certificates/images/backpack-logo.png'),
            'badges_icon': staticfiles_storage.url('certificates/images/ico-mozillaopenbadges.png'),
            'backpack_ui_img': staticfiles_storage.url('certificates/images/backpack-ui.png'),
            'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
            'social_platforms': settings.SOCIAL_PLATFORMS,
        },
        'show_program_listing': ProgramsApiConfig.is_enabled(),
        'show_dashboard_tabs': True,
        'disable_courseware_js': True,
        'nav_hidden': True,
        'records_url': get_credentials_records_url(),
        'courses': course_data,
        'user_extra_info': user_extra_info
    }

    if badges_enabled():
        context['data']['badges_api_url'] = reverse("badges_api:user_assertions", kwargs={'username': profile_username})

    return context
