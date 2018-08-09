from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from .models import ExtraInfo


class CheckNationalId(object):
    def process_request(self, request):
        set_national_id_url = reverse('set_national_id')
        logout_url = reverse('logout')

        is_set_national_id = set_national_id_url in request.path
        is_admin =  request.user.is_superuser
        is_logout_page = logout_url in request.path
        check_national_id_disabled = settings.FEATURES.get('DISABLE_CHECK_NATIONAL_ID', False)

        do_redirect = not (
            check_national_id_disabled
            or is_set_national_id
            or is_logout_page
            or is_admin
            or not request.user.is_authenticated()
            or ExtraInfo.has_national_id(request.user)
            or request.session.get('ws_federation_idp_name')
        )

        if do_redirect:
            return redirect(set_national_id_url)
