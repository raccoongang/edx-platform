"""
Slightly customized python-social-auth backend for SAML 2.0 support
"""
import logging

from base64 import b64encode
import random
import hashlib
import requests
import json
import urllib
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import Http404
from django.utils.functional import cached_property
from django.template.defaultfilters import slugify
from social_core.backends.saml import OID_EDU_PERSON_ENTITLEMENT, SAMLAuth, SAMLIdentityProvider
from social_core.exceptions import AuthForbidden, AuthFailed
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from defusedxml.lxml import tostring, fromstring
from lxml import etree

from openedx.core.djangoapps.theming.helpers import get_current_request

STANDARD_SAML_PROVIDER_KEY = 'standard_saml_provider'
SAP_SUCCESSFACTORS_SAML_KEY = 'sap_success_factors'
log = logging.getLogger(__name__)


class SAMLAuthBackend(SAMLAuth):  # pylint: disable=abstract-method
    """
    Customized version of SAMLAuth that gets the list of IdPs from third_party_auth's list of
    enabled providers.
    """
    name = "tpa-saml"

    def get_idp(self, idp_name):
        """ Given the name of an IdP, get a SAMLIdentityProvider instance """
        from .models import SAMLProviderConfig
        return SAMLProviderConfig.current(idp_name).get_config()

    def setting(self, name, default=None):
        """ Get a setting, from SAMLConfiguration """
        try:
            return self._config.get_setting(name)
        except KeyError:
            return self.strategy.setting(name, default, backend=self)

    def auth_url(self):
        """
        Check that SAML is enabled and that the request includes an 'idp'
        parameter before getting the URL to which we must redirect in order to
        authenticate the user.

        raise Http404 if SAML authentication is disabled.
        """
        if not self._config.enabled:
            log.error('SAML authentication is not enabled')
            raise Http404

        return super(SAMLAuthBackend, self).auth_url()

    def _check_entitlements(self, idp, attributes):
        """
        Check if we require the presence of any specific eduPersonEntitlement.

        raise AuthForbidden if the user should not be authenticated, or do nothing
        to allow the login pipeline to continue.
        """
        if "requiredEntitlements" in idp.conf:
            entitlements = attributes.get(OID_EDU_PERSON_ENTITLEMENT, [])
            for expected in idp.conf['requiredEntitlements']:
                if expected not in entitlements:
                    log.warning(
                        "SAML user from IdP %s rejected due to missing eduPersonEntitlement %s", idp.name, expected)
                    raise AuthForbidden(self)

    def _create_saml_auth(self, idp):
        """
        Get an instance of OneLogin_Saml2_Auth

        idp: The Identity Provider - a social_core.backends.saml.SAMLIdentityProvider instance
        """
        # We only override this method so that we can add extra debugging when debug_mode is True
        # Note that auth_inst is instantiated just for the current HTTP request, then is destroyed
        auth_inst = super(SAMLAuthBackend, self)._create_saml_auth(idp)
        from .models import SAMLProviderConfig
        if SAMLProviderConfig.current(idp.name).debug_mode:

            def wrap_with_logging(method_name, action_description, xml_getter):
                """ Wrap the request and response handlers to add debug mode logging """
                method = getattr(auth_inst, method_name)

                def wrapped_method(*args, **kwargs):
                    """ Wrapped login or process_response method """
                    result = method(*args, **kwargs)
                    log.info("SAML login %s for IdP %s. XML is:\n%s", action_description, idp.name, xml_getter())
                    return result
                setattr(auth_inst, method_name, wrapped_method)

            wrap_with_logging("login", "request", auth_inst.get_last_request_xml)
            wrap_with_logging("process_response", "response", auth_inst.get_last_response_xml)

        return auth_inst

    @cached_property
    def _config(self):
        from .models import SAMLConfiguration
        return SAMLConfiguration.current(Site.objects.get_current(get_current_request()))


class EdXSAMLIdentityProvider(SAMLIdentityProvider):
    """
    Customized version of SAMLIdentityProvider that can retrieve details beyond the standard
    details supported by the canonical upstream version.
    """

    def get_user_details(self, attributes):
        """
        Overrides `get_user_details` from the base class; retrieves those details,
        then updates the dict with values from whatever additional fields are desired.
        """
        details = super(EdXSAMLIdentityProvider, self).get_user_details(attributes)
        extra_field_definitions = self.conf.get('extra_field_definitions', [])
        details.update({
            field['name']: attributes[field['urn']][0] if field['urn'] in attributes else None
            for field in extra_field_definitions
        })
        return details


class SapSuccessFactorsIdentityProvider(EdXSAMLIdentityProvider):
    """
    Customized version of EdXSAMLIdentityProvider that knows how to retrieve user details
    from the SAPSuccessFactors OData API, rather than parse them directly off the
    SAML assertion that we get in response to a login attempt.
    """

    required_variables = (
        'sapsf_oauth_root_url',
        'sapsf_private_key',
        'odata_api_root_url',
        'odata_company_id',
        'odata_client_id',
    )

    @property
    def sapsf_idp_url(self):
        return self.conf['sapsf_oauth_root_url'] + 'idp'

    @property
    def sapsf_token_url(self):
        return self.conf['sapsf_oauth_root_url'] + 'token'

    @property
    def sapsf_private_key(self):
        return self.conf['sapsf_private_key']

    @property
    def odata_api_root_url(self):
        return self.conf['odata_api_root_url']

    @property
    def odata_company_id(self):
        return self.conf['odata_company_id']

    @property
    def odata_client_id(self):
        return self.conf['odata_client_id']

    def missing_variables(self):
        """
        Check that we have all the details we need to properly retrieve rich data from the
        SAP SuccessFactors OData API. If we don't, then we should log a warning indicating
        the specific variables that are missing.
        """
        if not all(var in self.conf for var in self.required_variables):
            missing = [var for var in self.required_variables if var not in self.conf]
            log.warning(
                "To retrieve rich user data for an SAP SuccessFactors identity provider, the following keys in "
                "'other_settings' are required, but were missing: %s",
                missing
            )
            return missing

    def get_odata_api_client(self, user_id):
        """
        Get a Requests session with the headers needed to properly authenticate it with
        the SAP SuccessFactors OData API.
        """
        session = requests.Session()
        assertion = session.post(
            self.sapsf_idp_url,
            data={
                'client_id': self.odata_client_id,
                'user_id': user_id,
                'token_url': self.sapsf_token_url,
                'private_key': self.sapsf_private_key,
            },
            timeout=10,
        )
        assertion.raise_for_status()
        assertion = assertion.text
        token = session.post(
            self.sapsf_token_url,
            data={
                'client_id': self.odata_client_id,
                'company_id': self.odata_company_id,
                'grant_type': 'urn:ietf:params:oauth:grant-type:saml2-bearer',
                'assertion': assertion,
            },
            timeout=10,
        )
        token.raise_for_status()
        token = token.json()['access_token']
        session.headers.update({'Authorization': 'Bearer {}'.format(token), 'Accept': 'application/json'})
        return session

    def get_user_details(self, attributes):
        """
        Attempt to get rich user details from the SAP SuccessFactors OData API. If we're missing any
        of the details we need to do that, fail nicely by returning the details we're able to extract
        from just the SAML response and log a warning.
        """
        details = super(SapSuccessFactorsIdentityProvider, self).get_user_details(attributes)
        if self.missing_variables():
            # If there aren't enough details to make the request, log a warning and return the details
            # from the SAML assertion.
            return details
        username = details['username']
        try:
            client = self.get_odata_api_client(user_id=username)
            response = client.get(
                '{root_url}User(userId=\'{user_id}\')?$select=username,firstName,lastName,defaultFullName,email'.format(
                    root_url=self.odata_api_root_url,
                    user_id=username
                ),
                timeout=10,
            )
            response.raise_for_status()
            response = response.json()
        except requests.RequestException:
            # If there was an HTTP level error, log the error and return the details from the SAML assertion.
            log.warning(
                'Unable to retrieve user details with username %s from SAPSuccessFactors with company ID %s.',
                username,
                self.odata_company_id,
            )
            return details
        return {
            'username': response['d']['username'],
            'first_name': response['d']['firstName'],
            'last_name': response['d']['lastName'],
            'fullname': response['d']['defaultFullName'],
            'email': response['d']['email'],
        }


class WsFederationBackend(SAMLAuthBackend):
    name = "tpa-ws-federation"
    _assertion_ns = 'urn:oasis:names:tc:SAML:2.0:assertion'

    def find_tag(self, path, elem, ns=None):
        el = elem
        for tag in path.split('/'):
            tag_name = ns and '{{{}}}{}'.format(ns, tag) or tag
            el = el.find(tag_name)
        return el

    def auth_url(self):
        from .models import SAMLProviderConfig
        idp_conf = SAMLProviderConfig.current(self.data['idp'])
        login_url = json.loads(idp_conf.other_settings or '{}').get('WS_FEDERATION_LOGIN_URL')
        self_url = 'http{}://{}/'.format(self.strategy.request_is_secure() and 's' or '', self.strategy.request_host())

        params = {
            'wtrealm': self_url,
            'wa': 'wsignin1.0',
            'wctx': self.get_wctx()
        }
        return '{}?{}'.format(login_url, urllib.urlencode(params))

    def check_hash(self, hash):
        salt = hash[:10]
        expect = hashlib.sha256('{}{}{}'.format(
            salt,
            settings.SECRET_KEY,
            self.strategy.session.session_key
        ))
        return (hash[10:] == expect.hexdigest())

    def get_wctx(self):
        salt = hex(random.randint(1099511627776, 2199023255551))[3:]
        hash = hashlib.sha256('{}{}{}'.format(
            salt,
            settings.SECRET_KEY,
            self.strategy.session.session_key
        ))
        return '{}/{}{}'.format(self.data['idp'], salt, hash.hexdigest())

    def pprint_xml(self, xml_string):
        xslt_tree = etree.XML('''
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
              <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
                <xsl:strip-space elements="*"/>
                <xsl:template match="/">
                  <xsl:copy-of select="."/>
                </xsl:template>
            </xsl:stylesheet>
        ''')
        transform = etree.XSLT(xslt_tree)
        return transform(xml_string)

    def ws_to_saml(self, resp, idp):
        from .models import SAMLProviderConfig
        samlp_conf = SAMLProviderConfig.current(idp.name)
        if samlp_conf.debug_mode:
            log.info('WS-Federation response: \n%s', self.pprint_xml(fromstring(resp)))

        response = fromstring(resp)
        tag = '{{{{{prefix}}}}}{{name}}'.format(prefix=response.nsmap[response.prefix])
        token_tag = tag.format(name='RequestedSecurityToken')
        token_type_tag = tag.format(name='TokenType')
        lifetime_tag = tag.format(name='Lifetime')
        resp_tag = tag.format(name='RequestSecurityTokenResponse')

        for el in response.getchildren():
            if el.tag == resp_tag:
                context = el.attrib['Context']

            for e in el.getchildren():
                if e.tag == token_tag:
                    saml_resp = e
                    issuer_val = self.find_tag('Assertion/Issuer', e, self._assertion_ns).text
                    nooa = self.find_tag('Assertion/Conditions', e, self._assertion_ns).attrib['NotOnOrAfter']
                    sp_id = self.find_tag('Assertion/Conditions/AudienceRestriction/Audience', e, self._assertion_ns).text
                elif e.tag == token_type_tag:
                    token_type = e.text
                elif e.tag == lifetime_tag:
                    created = filter(lambda x: x.tag == '{{{}}}{}'.format(x.nsmap[x.prefix], 'Created'), e.getchildren())
                    created = created and created[0].text or ''

        saml_resp.tag = '{urn:oasis:names:tc:SAML:2.0:protocol}Response'
        saml_resp.attrib['Version'] = '2.0'
        saml_resp.attrib['ID'] = slugify(context)
        saml_resp.attrib['IssueInstant'] = created

        saml_nm = saml_resp.nsmap
        saml_prefix = saml_resp.prefix

        status = etree.Element('{{{}}}Status'.format(saml_nm[saml_prefix]), nsmap=saml_nm)
        status_code = etree.Element(
            '{{{}}}StatusCode'.format(saml_nm[saml_prefix]),
            attrib={'Value': 'urn:oasis:names:tc:SAML:2.0:status:Success'},
            nsmap=saml_nm
        )
        status.append(status_code)
        issuer = etree.Element('Issuer', attrib={'xmlns': 'urn:oasis:names:tc:SAML:2.0:assertion'})
        issuer.text = issuer_val
        saml_resp.insert(0, status)
        saml_resp.insert(0, issuer)

        _sc = self.find_tag('Assertion/Subject/SubjectConfirmation', saml_resp, self._assertion_ns)
        current_url = '{}{}'.format(
            sp_id.endswith('/') and sp_id[:-1] or sp_id,
            self.strategy.request_path()
        )
        scd = etree.Element(
            'SubjectConfirmationData',
            attrib={'Recipient': current_url, 'NotOnOrAfter': nooa}
        )
        _sc.append(scd)

        if samlp_conf.debug_mode:
            log.info('Converted SAML2 response: \n%s', self.pprint_xml(saml_resp))

        return token_type, saml_resp

    def _create_saml_auth(self, idp):
        """Get an instance of OneLogin_Saml2_Auth"""
        config = self.generate_saml_config(idp)
        token_type, resp = self.ws_to_saml(self.strategy.request_post().get('wresult', ''), idp)

        if token_type != 'urn:oasis:names:tc:SAML:2.0:assertion':
            raise AuthFailed(self, 'SAML login failed: Unsupported token type.')

        post_data = {
            'SAMLResponse': b64encode(tostring(resp))
        }
        request_info = {
            'https': 'on' if self.strategy.request_is_secure() else 'off',
            'http_host': self.strategy.request_host(),
            'script_name': self.strategy.request_path(),
            'server_port': self.strategy.request_port(),
            'get_data': self.strategy.request_get(),
            'post_data': post_data,
        }

        from .models import SAMLProviderConfig
        idp_conf = SAMLProviderConfig.current(idp.name)
        cfg = json.loads(idp_conf.other_settings or '{}')
        return OneLogin_Saml2_Auth(request_info, config)

    def auth_complete(self, *args, **kwargs):
        """
        The user has been redirected back from the IdP and we should
        now log them in, if everything checks out.
        """

        data = self.strategy.request_data()
        wa = data.get('wa')
        wctx = data.get('wctx')
        wresult = data.get('wresult')
        if wa != 'wsignin1.0':
            raise AuthFailed(self, 'SAML login failed: Unknown action {}'.format(wa))

        wctx_list = wctx.split('/')
        hash = wctx_list[1]
        idp_name = wctx_list[0]

        if not self.check_hash(hash):
            raise AuthFailed(self, 'SAML login failed: Wrong response wctx')

        idp = self.get_idp(idp_name)
        auth = self._create_saml_auth(idp)
        auth.process_response()
        errors = auth.get_errors()
        if errors or not auth.is_authenticated():
            reason = auth.get_last_error_reason()
            raise AuthFailed(
                self, 'SAML login failed: {0} ({1})'.format(errors, reason)
            )

        attributes = auth.get_attributes()
        attributes['name_id'] = auth.get_nameid()
        self._check_entitlements(idp, attributes)
        response = {
            'idp_name': idp_name,
            'attributes': attributes,
            'session_index': auth.get_session_index(),
        }
        kwargs.update({'response': response, 'backend': self})
        self.strategy.session['ws_federation_idp_name'] = idp_name
        return self.strategy.authenticate(*args, **kwargs)


def get_saml_idp_choices():
    """
    Get a list of the available SAMLIdentityProvider subclasses that can be used to process
    SAML requests, for use in the Django administration form.
    """
    return (
        (STANDARD_SAML_PROVIDER_KEY, 'Standard SAML provider'),
        (SAP_SUCCESSFACTORS_SAML_KEY, 'SAP SuccessFactors provider'),
    )


def get_saml_idp_class(idp_identifier_string):
    """
    Given a string ID indicating the type of identity provider in use during a given request, return
    the SAMLIdentityProvider subclass able to handle requests for that type of identity provider.
    """
    choices = {
        STANDARD_SAML_PROVIDER_KEY: EdXSAMLIdentityProvider,
        SAP_SUCCESSFACTORS_SAML_KEY: SapSuccessFactorsIdentityProvider,
    }
    if idp_identifier_string not in choices:
        log.error(
            '%s is not a valid EdXSAMLIdentityProvider subclass; using EdXSAMLIdentityProvider base class.',
            idp_identifier_string
        )
    return choices.get(idp_identifier_string, EdXSAMLIdentityProvider)
