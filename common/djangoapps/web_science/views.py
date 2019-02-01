from django.http import HttpResponse
from django.views.generic import View
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import UsageKey

from courseware.access import has_access
from openedx.core.lib.url_utils import unquote_slashes
from web_science.models import WebScienceUnitLog
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError


class WebScienceUnitLogView(View):

    def get(self, *args, **kwargs):
        try:
            usage_key = UsageKey.from_string(unquote_slashes(kwargs.pop('usage_id')))
        except InvalidKeyError:
            return HttpResponse('unit not found', status=404)

        try:
            user = self.request.user
            unit = modulestore().get_item(usage_key)
            if has_access(user, 'load', unit, course_key=usage_key.course_key):
                log = WebScienceUnitLog.log(user, usage_key)
                return HttpResponse(log.updated_at)
        except ItemNotFoundError:
            pass
        return HttpResponse('access denied {}'.format(usage_key), status=403)
