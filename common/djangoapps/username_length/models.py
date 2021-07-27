from django.contrib.auth.models import User

from openedx.core.djangoapps.user_api.accounts import USERNAME_MAX_LENGTH


User._meta.get_field('username').max_length = USERNAME_MAX_LENGTH
