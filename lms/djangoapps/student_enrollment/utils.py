"""
This module contains some handy utility functions for
creating/registering users, as well as sending emails.
"""

from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import get_connection
from django.template.loader import render_to_string
import requests
from student.models import UserProfile


def create_user_profile(user, full_name):
    """
    A small helper function for creating a user profile

    `user` is the User instance that we want to create a user profile for
    `full_name` is the full name of the person that we are creating the
        profile for
    """
    user_profile = UserProfile(user=user)
    user_profile.full_name = full_name
    user_profile.save()


def register_student(email, full_name, password=None):
    """
    Register a new user with a randomly generated password

    `email` is the email address of the student
    `full_name` is the full name of the student
    `password` is the password to be used when creating the new user. If
        a password is not provided then a password will be generated for
        that student.

    Returns the user and None if the a password is provided
    Returns the user and the auto-generated password if a password was
        not provided
    """
    username = email
    
    if password:
        user = User.objects.create_user(username, email, password)
        create_user_profile(user, full_name)
        return user, None
    else:
        password = User.objects.make_random_password()
        user = User.objects.create_user(username, email, password)
        create_user_profile(user, full_name)
        return user, password


def get_or_register_student(email, full_name, password=None):
    """
    Check to see if the user already exists within the LMS and creates
    the user if it doesn't already exist.

    If the student already exists in the system then this is considered to
    be a re-enrollment, but if this are not already registered then they
    will be enrolled.
    
    `user` is an object that should at least contain an email and
        a full_name property

    Returns a user instance, the user's password and the enrollment type.
    """
    try:
        user = User.objects.get(email=email)
        try:
            user.program_set.first().program_code == "5DCC"
            return user, None, 3
        except AttributeError:
            return user, None, 2
    except User.DoesNotExist:
        user, password = register_student(email, full_name, password)
        return user, password, 0


def create_email_connection():
    """
    Create a new SMTP connection using the SMTP settings

    Returns a new SMTP connection
    """
    host = settings.EMAIL_HOST
    port = settings.EMAIL_PORT
    username = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    use_tls = settings.EMAIL_USE_TLS

    connection = get_connection(host=host, port=port,
                                username=username, password=password, 
                                use_tls=use_tls)
    return connection


def construct_email(to_address, from_address, template_location, **kwargs):
    """
    Constuct the context of the email and inject it into the HTML email.

    `to_address` is the address that the email is being sent to
    `from_address` is the address that the email is being sent from
    `template_location` is the path to the template file

    Returns the HTML email that's to be sent (with the inject template context)
    """
    context = {
        'email': to_address
    }
    context.update(kwargs)

    html_content = render_to_string(template_location, context).encode(
        "utf-8")

    return html_content


def post_to_zapier(zap_url, data):
    """
    Post data to Zapier. This function is a layer of abstraction on top
    of Zapier.

    `zap_url` is the endpoint that we wish to hit
    `data` is a dictionary that contains the data that we wish to post
        to Zapier
    """
    response = requests.post(zap_url, data=data)
