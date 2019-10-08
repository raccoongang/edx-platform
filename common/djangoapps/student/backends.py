from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.core.djangoapps.site_configuration.helpers import is_site_configuration_enabled
from student.models import UserSites


class MainSiteBackend(ModelBackend):
    """
    User can log in to the base/main site (example.com).
    Note: superusers (Bussnies admin) can log into any site.
    """
    def authenticate(self, *args, **kwargs):
        user = super(MainSiteBackend, self).authenticate(*args, **kwargs)

        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if user:
            if is_default_site:
                return user
            if user.is_superuser:
                return user
        return None


class SiteMemberBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check whether the user has access to the site.
    Note: superusers (Bussnies admin) can log into any site.
    """
    def authenticate(self, *args, **kwargs):
        try:
            user = super(SiteMemberBackend, self).authenticate(*args, **kwargs)
            site = get_current_site()
            if UserSites.objects.get(user=user, site=site):
                return user
            return None
        except UserSites.DoesNotExist:
            return None
