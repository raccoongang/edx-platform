"""
Helper for Admin Dashboard
"""

from django.contrib.auth.models import User
from student.models import Registration, UserProfile
from student.helpers import link_user_with_site
from student.models import UserSites
from django.contrib.sites.models import Site
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings


def create_user_and_link_with_subdomain(email, username, site_id, password):
    """
    Create a new user, add a new Registration instance for letting user verify its identity and create a user profile.

    :param email: user's email address
    :param username: user's username
    :param password: user's password

    :return: User instance of the new user.
    """
    try:
        user = User.objects.create_user(username, email, password)
        reg = Registration()
        reg.register(user)

        profile = UserProfile(user=user)
        profile.save()

        add_user_to_site(user, site_id)

        return user
    except Exception as e:
        return e


def add_user_to_site(user, site_id):
    """
    Link user with the initial site he signed-up from
    :param site:
    :param user:
    """
    try:
        site = Site.objects.get(id=site_id)
        UserSites.objects.create(user=user, site=site)

    except Exception as e:
        return e


def send_registration_email(email):

    subject = "Registration Email"
    from_email = configuration_helpers.get_value('email_from_address',
                                                 settings.DEFUALT_FROM_EMAIL)
    message = ""

    pass
