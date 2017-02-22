import hashlib
from uuid import uuid4

from django.conf import settings


def hashkey_generator():
    """
    Generate a hashkey for Referral link.
    """
    hash = hashlib.sha1(uuid4().hex.encode('utf-8'))
    hash.update(settings.SECRET_KEY.encode('utf-8'))
    return hash.hexdigest()[::2]
