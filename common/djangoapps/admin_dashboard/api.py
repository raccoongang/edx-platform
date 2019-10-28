import re
import string
import random
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt
from django.views.decorators.cache import cache_control
from util.json_request import JsonResponse
# from lms.djangoapps.instructor.views.api import _split_input_list, generate_unique_password
from helpers import create_user_and_link_with_subdomain, send_registration_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import logging


logger = logging.getLogger(__name__)

# @require_POST
# # @ensure_csrf_cookie
# @cache_control(no_cache=True, no_store=True, must_revalidate=True)
@csrf_exempt
def create_bulk_users(request):
    try:
   
        users_emails = _split_input_list(request.GET.get('emails'))
        site_id = request.GET.get('subdomain')

        generated_passwords = []
        created_users = []
        for email in users_emails:
            validate_email(email)
            username = email
            # country = "Saudi Arabia"

            password = generate_unique_password(generated_passwords)
            user = create_user_and_link_with_subdomain(
                email, username, site_id, password,
            )
            created_users.append(user.email)

            # send_registration_email(email)

        return JsonResponse(created_users)

    except ValidationError:
        return JsonResponse(status=500)

    except Exception as e:
        logger.error(e)
        return JsonResponse()


def _split_input_list(str_list):
    """
    Separate out individual student email from the comma, or space separated string.

    e.g.
    in: "Lorem@ipsum.dolor, sit@amet.consectetur\nadipiscing@elit.Aenean\r convallis@at.lacus\r, ut@lacinia.Sed"
    out: ['Lorem@ipsum.dolor', 'sit@amet.consectetur', 'adipiscing@elit.Aenean', 'convallis@at.lacus', 'ut@lacinia.Sed']

    `str_list` is a string coming from an input text area
    returns a list of separated values
    """

    new_list = re.split(r'[\n\r\s,]', str_list)
    new_list = [s.strip() for s in new_list]
    new_list = [s for s in new_list if s != '']

    return new_list


def generate_unique_password(generated_passwords, password_length=12):
    """
    generate a unique password for each student.
    """

    password = generate_random_string(password_length)
    while password in generated_passwords:
        password = generate_random_string(password_length)

    generated_passwords.append(password)

    return password


def generate_random_string(length):
    """
    Create a string of random characters of specified length
    """
    chars = [
        char for char in string.ascii_uppercase + string.digits + string.ascii_lowercase
        if char not in 'aAeEiIoOuU1l'
    ]

    return string.join((random.choice(chars) for __ in range(length)), '')
