"""
Common branding views for both LMS and Studio.
"""
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


class FaviconRedirectView(RedirectView):
    """
    Theme-aware redirect view for favicon.
    """
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.url = staticfiles_storage.url('images/favicon.ico')
        return super().get_redirect_url(*args, **kwargs)
