"""
Django template context processors.
"""

import third_party_auth


def tpa_hint_context(request):
    """
    TPA hint context for django templates.
    """
    return {
        'tpa_hint': get_auth0_provider_id() if hasattr(request, 'user') and not request.user.is_authenticated() else None
    }


def get_auth0_provider_id():
    """
    Get Auth0 provider id if configured and enabled.

    Returns:
        Auth0 provider id (str) or `None` if configuration is not enabled.
    """
    if third_party_auth.is_enabled():
        for enabled in third_party_auth.provider.Registry.displayed_for_login():
            if enabled.is_auth0():
                return enabled.provider_id
