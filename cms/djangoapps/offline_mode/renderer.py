"""
This module contains the XBlockRenderer class,
which is responsible for rendering an XBlock HTML content from the LMS.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest

from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore

from common.djangoapps.edxmako.shortcuts import render_to_string
from cms.djangoapps.contentstore.views.preview import get_preview_fragment, StudioPartitionService
from xblock.runtime import KvsFieldData
from cms.djangoapps.contentstore.views.session_kv_store import SessionKeyValueStore
from functools import partial
from lms.djangoapps.lms_xblock.field_data import LmsFieldData
from common.djangoapps.xblock_django.user_service import DjangoXBlockUserService
from cms.djangoapps.contentstore.utils import StudioPermissionsService, get_visibility_partition_info
from cms.djangoapps.contentstore.views.access import get_user_role
from cms.djangoapps.contentstore.views.session_kv_store import SessionKeyValueStore


import logging
from functools import partial

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.locator import LibraryContainerLocator
from rest_framework.request import Request
from web_fragments.fragment import Fragment
from xblock.django.request import django_to_webob_request, webob_to_django_response
from xblock.exceptions import NoSuchHandlerError
from xblock.runtime import KvsFieldData

from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError, ProcessingError
from xmodule.modulestore.django import XBlockI18nService, modulestore
from xmodule.partitions.partitions_service import PartitionService
from xmodule.services import SettingsService, TeamsConfigurationService
from xmodule.studio_editable import has_author_view
from xmodule.util.sandboxing import SandboxService
from xmodule.util.builtin_assets import add_webpack_js_to_fragment
from xmodule.x_module import AUTHOR_VIEW, PREVIEW_VIEWS, STUDENT_VIEW, XModuleMixinfrom cms.djangoapps.xblock_config.models import StudioConfig
from cms.djangoapps.contentstore.toggles import individualize_anonymous_user_id
from cms.lib.xblock.field_data import CmsFieldData
from cms.lib.xblock.upstream_sync import UpstreamLink
from common.djangoapps.static_replace.services import ReplaceURLService
from common.djangoapps.static_replace.wrapper import replace_urls_wrapper
from common.djangoapps.student.models import anonymous_id_for_user
from common.djangoapps.edxmako.shortcuts import render_to_string
from common.djangoapps.edxmako.services import MakoService
from common.djangoapps.xblock_django.user_service import DjangoXBlockUserService
from lms.djangoapps.lms_xblock.field_data import LmsFieldData
from openedx.core.lib.license import wrap_with_license
from openedx.core.lib.cache_utils import CacheService
from openedx.core.lib.xblock_utils import (
    request_token,
    wrap_fragment,
    wrap_xblock,
    wrap_xblock_aside
)

from .utils import get_offline_service_user

User = get_user_model()
log = logging.getLogger(__name__)


class XBlockRenderer:
    """
    Renders an XBlock HTML content from the LMS.
    Since imports from LMS are used here, XBlockRenderer can be called only in the LMS runtime.
    :param usage_key_string: The string representation of the block UsageKey.
    :param user: The user for whom the XBlock will be rendered.
    """

    def __init__(self, usage_key_string, user=None, request=None):
        self.usage_key = UsageKey.from_string(usage_key_string)
        self.usage_key = self.usage_key.replace(
            course_key=modulestore().fill_in_run(self.usage_key.course_key)
        )
        self.user = user or get_offline_service_user()
        self.request = request or self.generate_request()

    def generate_request(self):
        """
        Generates a request object with the service user and a session.
        """
        request = HttpRequest()
        request.user = self.user
        session = SessionStore()
        session.create()
        request.session = session
        request.LANGUAGE_CODE = "en"
        return request

    def render_xblock_from_lms(self):
        course_key = self.usage_key.course_key

        with modulestore().bulk_operations(course_key):
            block = modulestore().get_item(self.usage_key)

            block = self._prepare_block(self.request, block)

            req_token = request_token(self.request)
            fragment = self.get_fragment(block)
            fragment.js_init_fn = 'XBlockToXModuleShim'
            fragment.json_init_args = {"xmodule-type": "Problem"}

            wrapped_fragment = wrap_xblock(
                runtime_class='LmsRuntime',
                block=block,
                view='student_view',
                frag=fragment,
                context={},
                usage_id_serializer=str,
                request_token=req_token,
                display_name_only=False,
                extra_data={}
            )

            context = {
                "fragment": wrapped_fragment,
                "block": block,
            }

            return render_to_string(
                "offline_container.html",
                context,
                namespace="main",
            )

    @staticmethod
    def get_fragment(block, wrap_xblock_data=None):
        """
        Returns the HTML fragment of the XBlock.
        """
        student_view_context = {
            "show_bookmark_button": "0",
            "show_title": "1",
            "hide_access_error_blocks": True,
            "is_mobile_app": True,
        }
        if wrap_xblock_data:
            student_view_context["wrap_xblock_data"] = wrap_xblock_data
        return block.render("student_view", context=student_view_context)

    def _prepare_block(self, request, block):
        from xmodule.util.sandboxing import SandboxService
        from xmodule.contentstore.django import contentstore
        from openedx.core.lib.cache_utils import CacheService
        from django.core.cache import cache

        student_data = KvsFieldData(SessionKeyValueStore(request))

        wrapper = partial(LmsFieldData, student_data=student_data)

        block.bind_for_student(request.user.id, [wrapper])

        mako_service = MakoService(namespace_prefix='lms.')

        services = {
            "studio_user_permissions": StudioPermissionsService(request.user),
            "i18n": XBlockI18nService,
            'mako': mako_service,
            "settings": SettingsService(),
            "user": DjangoXBlockUserService(
                request.user,
                user_role=get_user_role(request.user, self.usage_key.course_key),
            ),
            "partitions": StudioPartitionService(course_id=self.usage_key.course_key),
            "teams_configuration": TeamsConfigurationService(),
            "sandbox": SandboxService(contentstore=contentstore, course_id=self.usage_key.course_key),
            "cache": CacheService(cache),
            'replace_urls': ReplaceURLService
        }

        block.runtime.mixins = settings.XBLOCK_MIXINS

        block.runtime._services.update(services)  # pylint: disable=protected-access
        return block
