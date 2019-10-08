from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_control
from util.json_request import JsonResponse
from lms.djangoapps.instructor.views.api import _split_input_list, generate_unique_password
from admin_dashboard.helpers import create_user_and_link_with_subdomain, send_registration_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail


# @require_POST
# # @ensure_csrf_cookie
# @cache_control(no_cache=True, no_store=True, must_revalidate=True)
def create_bulk_users(request):
    try:
        emails_raw = validate_email(request.GET.get('emails'))

        users_emails = _split_input_list(emails_raw)
        site_id = request.GET.get('subdomain')

        generated_passwords = []
        created_users = []
        for email in users_emails:
            username = email
            # country = "Saudi Arabia"

            password = generate_unique_password(generated_passwords)
            user = create_user_and_link_with_subdomain(
                email, username, site_id, password,
            )
            created_users.append(user.email)

            send_registration_email(email)

        return JsonResponse(created_users)

    except ValidationError:
        return JsonResponse(status=500)

    except Exception as e:
        return JsonResponse()
