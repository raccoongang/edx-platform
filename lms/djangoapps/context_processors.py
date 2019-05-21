"""
Django Template Context Processor for LMS Online Contextual Help
"""
import logging
import urllib3
import xmltodict
import ConfigParser
from django.conf import settings

from util.help_context_processor import common_doc_url
from urllib3.exceptions import MaxRetryError


logger = logging.getLogger(__file__)


# Open and parse the configuration file when the module is initialized
CONFIG_FILE = open(settings.REPO_ROOT / "docs" / "lms_config.ini")
CONFIG = ConfigParser.ConfigParser()
CONFIG.readfp(CONFIG_FILE)


def doc_url(request=None):  # pylint: disable=unused-argument
    """
    This function is added in the list of TEMPLATES 'context_processors' OPTION, which is a django setting for
    a tuple of callables that take a request object as their argument and return a dictionary of items
    to be merged into the RequestContext.

    This function returns a dict with get_online_help_info, making it directly available to all mako templates.

    Args:
        request: Currently not used, but is passed by django to context processors.
            May be used in the future for determining the language of choice.
    """
    return common_doc_url(request, CONFIG)


def xml_header_and_footer(request):
    """
    Renders a custom html header and footer, received from the Microsoft's side.

    :request: HttpRequest object instance that was passed from the view
    :returns: dictionary of the four filters ('xml_css_includes', 'xml_js_includes', `xml_header`, `xml_footer`)
              added by this context processor
    """
    try:
        connection = urllib3.connection_from_url('https://uhf.microsoft.com')
        response = connection.request(
            'get',
            settings.FOURAFRIKA_XML_URL,
        )
        raw_xml_dict = xmltodict.parse(response.data)
        xml_dict = raw_xml_dict['shell']
    except MaxRetryError:
        xml_dict = {
            'cssIncludes': '',
            'javascriptIncludes': '',
            'headerHtml': '',
            'footerHtml': '',
        }
        logger.exception('Connect to the header/footer xml resource failed')

    filters = {
        'xml_css_includes': xml_dict.get('cssIncludes'),
        'xml_js_includes': xml_dict.get('javascriptIncludes'),
        'xml_header': xml_dict.get('headerHtml'),
        'xml_footer': xml_dict.get('footerHtml'),
    }
    return filters
