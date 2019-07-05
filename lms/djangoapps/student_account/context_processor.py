from django.core.urlresolvers import reverse

import third_party_auth
from third_party_auth import pipeline

from student.helpers import get_next_url_for_login_page
from .views import account_settings_context


def context_providers(request):
    context = {
        'providers': []
    }
    redirect_to = get_next_url_for_login_page(request)
    if third_party_auth.is_enabled():
        for enabled in third_party_auth.provider.Registry.displayed_for_login():
            info = {
                "id": enabled.provider_id,
                "name": enabled.name,
                "iconClass": enabled.icon_class or None,
                "iconImage": enabled.icon_image.url if enabled.icon_image else None,
                "loginUrl": pipeline.get_login_url(
                    enabled.provider_id,
                    pipeline.AUTH_ENTRY_LOGIN,
                    redirect_url=redirect_to,
                ),
                "registerUrl": pipeline.get_login_url(
                    enabled.provider_id,
                    pipeline.AUTH_ENTRY_REGISTER,
                    redirect_url=redirect_to,
                ),
            }
            context["providers" if not enabled.secondary else "secondaryProviders"].append(info)
    return context
