"""
MFE API Views for useful information related to mfes.
"""

import edx_api_doc_tools as apidocs
from django.conf import settings
from django.http import HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.views import APIView

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


class MFEConfigView(APIView):
    """
    Provides an API endpoint to get the MFE configuration from settings (or site configuration).
    """

    @method_decorator(cache_page(settings.MFE_CONFIG_API_CACHE_TIMEOUT))
    @apidocs.schema(
        parameters=[
            apidocs.query_parameter(
                'mfe',
                str,
                description="Name of an MFE (a.k.a. an APP_ID).",
            ),
        ],
    )
    def get(self, request):
        """
        Return the MFE configuration, optionally including MFE-specific overrides.

        **Usage**

          Get common config:
          GET /api/mfe_config/v1

          Get app config (common + app-specific overrides):
          GET /api/mfe_config/v1?mfe=name_of_mfe

        **GET Response Values**
        ```
        {
            "BASE_URL": "https://name_of_mfe.example.com",
            "LANGUAGE_PREFERENCE_COOKIE_NAME": "example-language-preference",
            "CREDENTIALS_BASE_URL": "https://credentials.example.com",
            "DISCOVERY_API_BASE_URL": "https://discovery.example.com",
            "LMS_BASE_URL": "https://courses.example.com",
            "LOGIN_URL": "https://courses.example.com/login",
            "LOGOUT_URL": "https://courses.example.com/logout",
            "STUDIO_BASE_URL": "https://studio.example.com",
            "LOGO_URL": "https://courses.example.com/logo.png",
            ... and so on
        }
        ```
        """

        if not settings.ENABLE_MFE_CONFIG_API:
            return HttpResponseNotFound()

        mfe_config = configuration_helpers.get_value('MFE_CONFIG', settings.MFE_CONFIG)
        if request.query_params.get('mfe'):
            mfe = str(request.query_params.get('mfe'))

            if mfe == 'catalog':
                _update_config_for_catalog(mfe_config)

            app_config = configuration_helpers.get_value(
                'MFE_CONFIG_OVERRIDES',
                settings.MFE_CONFIG_OVERRIDES,
            )
            mfe_config.update(app_config.get(mfe, {}))
        return JsonResponse(mfe_config, status=status.HTTP_200_OK)


def _update_config_for_catalog(mfe_config):
    """
    Update the MFE config for the catalog MFE with values from the site configuration.

    This is done for backward compatibility with the old configuration system.
    """
    catalog_conf = {
        'enable_course_sorting_by_start_date': configuration_helpers.get_value(
            'ENABLE_COURSE_SORTING_BY_START_DATE',
            settings.FEATURES['ENABLE_COURSE_SORTING_BY_START_DATE'],
        ),
        'homepage_overlay_html': configuration_helpers.get_value('homepage_overlay_html'),
        'show_partners': configuration_helpers.get_value('show_partners', True),
        'show_homepage_promo_video': configuration_helpers.get_value('show_homepage_promo_video', False),
        'homepage_course_max': configuration_helpers.get_value(
            'HOMEPAGE_COURSE_MAX', settings.HOMEPAGE_COURSE_MAX
        ),
        'homepage_promo_video_youtube_id': configuration_helpers.get_value(
            'homepage_promo_video_youtube_id', '<your-youtube-id>'
        ),
    }
    for key, value in catalog_conf.items():
        mfe_config[key] = mfe_config.get(key, value)  # add value from site configuration if not set
