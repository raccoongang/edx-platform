"""
Utility functions for offline mode.
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()
log = logging.getLogger(__name__)


def get_offline_service_user():
    """
    Get the service user to render XBlock.
    """
    try:
        return User.objects.get(username=settings.OFFLINE_SERVICE_WORKER_USERNAME)
    except User.DoesNotExist as e:
        log.error(
            f'Service user with username {settings.OFFLINE_SERVICE_WORKER_USERNAME} to render XBlock does not exist.'
        )
        raise e

from urllib.parse import urlparse, unquote

NON_ASSET_SCHEMES = ("http://", "https://", "data:", "mailto:", "tel:")

def normalize_course_asset_path(raw: str) -> str | None:
    """
    Приводить raw /assets/... або подібний шлях до відносного імені файлу в course assets.
    Повертає None, якщо це не курс-асет (зовнішній лінк, data:, порожнє).
    """
    if not raw:
        return None
    raw = raw.strip()

    # Відсікаємо явні не-асети
    if raw.startswith(NON_ASSET_SCHEMES) or raw.startswith("#"):
        return None

    # Розібрати URL і взяти тільки path, без query/fragment
    parsed = urlparse(raw)
    path = parsed.path or ""
    if not path:
        return None

    path = unquote(path)

    # Зрізати відомі префікси
    for pref in ("/assets/", "assets/"):
        if path.startswith(pref):
            path = path[len(pref):]
            break

    # Захист від початкового слеша
    path = path.lstrip("/")

    # Відсіяти службові каталоги (не course assets)
    if not path or path.startswith(("media/", "static/")):
        return None

    return path