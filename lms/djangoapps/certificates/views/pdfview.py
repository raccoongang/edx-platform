"""
Custom PDF certificates logic.
"""
import logging
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from edxmako.shortcuts import render_to_string
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from xhtml2pdf import pisa
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from webview import (
    _get_user_certificate,
    _update_badge_context,
    _update_certificate_context,
    _update_configuration_context,
    _update_context_with_basic_info,
    _update_context_with_user_info,
    _update_course_context,
    _update_grading_context,
    _update_organization_context,
    _update_social_context,
    get_active_web_certificate,
    get_certificate_footer_context,
    get_certificate_header_context,

)
from certificates.models import CertificateHtmlViewConfiguration

log = logging.getLogger(__name__)


def _prepare_pdf_content(template_rel_path, context, html=None):
    """
    Create a content for a pdf document.
    """
    html = html or render_to_string(template_rel_path, context)
    result = BytesIO()
    # FIXME cyrillic https://stackoverflow.com/a/2147026
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding="UTF-8")
    return result, pdf


def _prepare_pdf_file_response(template_rel_path, context, user_id, course_id, html=None):
    """
    Process the content and return a pdf file in the http response.
    """
    result, pdf = _prepare_pdf_content(template_rel_path, context, html)

    if pdf.err:
        log.error(
            "An error happened while preparing certificate pdf: %s."
            "User id: %d, course: %s",
            str(pdf.err),
            str(user_id),
            str(course_id),
        )
        return HttpResponse('')
    else:
        return HttpResponse(result.getvalue(), content_type='application/pdf')


@login_required
def download_certificate_pdf(request, user_id, course_id):
    """
    Handle a request to download a certificate in the pdf form.
    """
    template_rel_path = "certificates/valid.html"
    invalid_template_path = 'certificates/invalid.html'
    platform_name = configuration_helpers.get_value("platform_name", settings.PLATFORM_NAME)
    html = None

    # Populate the context in the same way it's done for webview certificates.
    context = {"is_pdf": True}
    configuration = CertificateHtmlViewConfiguration.get_config()
    _update_context_with_basic_info(context, course_id, platform_name, configuration)

    # We handle exceptions just in case.
    # A user usually gets here from the certificate view page,
    # so it's quite unlikely to run into exceptions below.

    try:
        course_key = CourseKey.from_string(course_id)
        user = User.objects.get(id=user_id)
        course = modulestore().get_course(course_key)
    except (InvalidKeyError, ItemNotFoundError, User.DoesNotExist) as exception:
        error_str = (
            "Invalid cert: error finding course %s or user with id "
            "%d. Specific error: %s"
        )
        log.info(error_str, course_id, user_id, str(exception))
        html = render_to_string(invalid_template_path, context)
        return _prepare_pdf_file_response(template_rel_path, context, user_id, course_id, html)

    user_certificate = _get_user_certificate(request, user, course_key, course)
    if not user_certificate:
        log.info(
            "Invalid cert: User %d does not have eligible cert for %s.",
            user_id,
            course_id,
        )
        html = render_to_string(invalid_template_path, context)
        return _prepare_pdf_file_response(template_rel_path, context, user_id, course_id, html)

    active_configuration = get_active_web_certificate(course)
    if active_configuration is None:
        log.info(
            "Invalid cert: course %s does not have an active configuration. User id: %d",
            course_id,
            user_id,
        )
        html = render_to_string(invalid_template_path, context)
        return _prepare_pdf_file_response(template_rel_path, context, user_id, course_id, html)

    context['certificate_data'] = active_configuration
    context.update(configuration.get(user_certificate.mode, {}))
    _update_organization_context(context, course)
    _update_course_context(request, context, course, platform_name)
    _update_context_with_user_info(context, user, user_certificate)
    _update_social_context(request, context, course, user, user_certificate, platform_name)
    _update_certificate_context(context, user_certificate, platform_name)
    _update_badge_context(context, course, user)
    _update_configuration_context(context, configuration)
    context.update(get_certificate_header_context(is_secure=request.is_secure()))
    context.update(get_certificate_footer_context())
    context.update(course.cert_html_view_overrides)
    _update_grading_context(context, course, user)

    return _prepare_pdf_file_response(template_rel_path, context, user_id, course_id, html)
