""" Views for a student's profile information. """
import requests
import json
from badges.utils import badges_enabled
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django_countries import countries

from edeos.api_calls import ALLOWED_EDEOS_API_ENDPOINTS_NAMES, EdeosApiClient
from edeos.utils import (get_user_id, get_user_id_from_email,
                         send_edeos_api_request)
from edxmako.shortcuts import marketing_link, render_to_response
from openedx.core.djangoapps.site_configuration import \
    helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.api import get_account_settings
from openedx.core.djangoapps.user_api.errors import (UserNotAuthorized,
                                                     UserNotFound)
from openedx.core.djangoapps.user_api.preferences.api import \
    get_user_preferences

from student.models import User, UserProfile, CourseEnrollment


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

    try:
        return render_to_response(
            'student_profile/learner_profile.html',
            learner_profile_context(request, username, request.user.is_staff)
        )
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
    active_course = CourseEnrollment.objects.filter(user=profile_user.id).filter(is_active=True)

    d = {
        "payload": {
            'student_id': get_user_id(request.user),
            'client_id': getattr(settings, 'EDEOS_API_KEY'),
        },
        "api_endpoint": "wallet_balance",
        "key": getattr(settings, 'EDEOS_API_KEY'),
        "secret": getattr(settings, 'EDEOS_API_SECRET'),
        "base_url": getattr(settings, 'EDEOS_API_URL')
    }
    edeos_resp = send_edeos_api_request(**d)
    context = {
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
            'active_course': True if active_course else False,
            # Skillonomy customization.
            # Branding/environments tend to update (Edeos, Mobytize, Protifonomy)
            'edeos_balance': edeos_resp,
            "mobytize_token": profile_user.profile.mobytize_token,
            "users": profile_user.profile.mobytize_id,
            "wallets_data": get_user_wallets_data(profile_user),
        },
        'disable_courseware_js': True,
        # Skillonomy customization
        "display_wallets_data": profile_user.is_active and own_profile and settings.FEATURES["DISPLAY_WALLETS"],
    }

    if badges_enabled():
        context['data']['badges_api_url'] = reverse("badges_api:user_assertions", kwargs={'username': profile_username})

    return context


def get_user_wallets_data(requesting_user):
    """
    Get wallets data for a user.
    """
    profile = UserProfile.objects.get(user=requesting_user)
    return {
        "profitonomy_public_key": profile.profitonomy_public_key if profile else "",
        "wallet_name": profile.wallet_name if profile else "",
    }


def learner_profile_statistics_context(profile_username, profile_statistics):
    """Context for the learner student_profile/profile_statistics.html page.

    Args:
        profile_username (str): username of user whose profile is requested.
        profile_statistics (str): html in string

    Returns:
        dict
    """
    context = {
        'data': {
            'error_message': '',
            'profile_statistics': profile_statistics,
            'username': profile_username,
            },
    }


    return context

def learner_performance(request, course_id=None, student_id=None):
    """
        view for maiking request on mobytize platform
    """
    if student_id:
        student = User.objects.get(id=int(student_id))
    else:
        student = request.user

    date_from = CourseEnrollment.objects.filter(user=student.id).filter(is_active=True).order_by('created').first()

    if date_from:
        date_to = datetime.today()
        date_to = date_to.strftime("%Y-%m-%d")
        date_from = date_from.created.strftime("%Y-%m-%d")
    else:
        return render_to_response('static_templates/403.html')

    edeos_post_data = {
        "payload": {
            "date_from":date_from,
            "date_to":date_to,
            "type": 0 if request.user.is_staff else 1,
            "mobytize_token":student.profile.mobytize_token,
            "users":student.profile.mobytize_id
        },
        "api_endpoint": "profile_statistics",
        "key": getattr(settings, 'EDEOS_API_KEY'),
        "secret": getattr(settings, 'EDEOS_API_SECRET'),
        "base_url": getattr(settings, 'EDEOS_API_URL')
    }

    response = send_edeos_api_request(**edeos_post_data)

    try:
        return render_to_response(
            'student_profile/learner_performance.html',
            learner_profile_statistics_context(student.username, response)
        )
    except (UserNotAuthorized, UserNotFound, ObjectDoesNotExist):
        raise Http404

def profile_statistics(request, username):
    """
        view render profile statistics page where will be iframe with user statistics
    """
    if request.user.get_username() == username:
        return render_to_response('student_profile/profile_statistics.html',
                                  learner_profile_statistics_context(username, request))
    else:
        return render_to_response('static_templates/403.html')
