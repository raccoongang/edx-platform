"""
Client to deal with SMS provider
"""
import logging
from urllib import quote_plus
from urlparse import urljoin

from django.conf import settings
import requests


log = logging.getLogger(__name__)

ERR_99 = '99' # 'User Does not exist'
ERR_100 = '100' # 'unsuccessful authentication'
ERR_101 = '101' # 'invalid action'
ERR_102 = '102' # 'one or more empty fileds'
ERR_200 = '200' # 'sending sms failed'
ERR_201 = '201' # 'no or the message is empty'
ERR_400 = '400' # 'Non-existing reception report'

STATUS_OK = 'OK'
STATUS_ERROR = 'ERR'


class Singletone(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class SMSClient(Singletone):
    """
    Client for handling different types of requests.
    """
    ACCESS_TOKEN_TEMPLATE = '/token/{username}/{password}'
    SEND_MESSAGE_TEMPLATE = '/trimite/{username}/{token}/Q1/{number}/{message}'
    CREDIT_TEMPLATE = '/credit/{username}/{token}/'
    MESSAGE_STATUS_TEMPLATE = '/status/{username}/{token}/{queue}'

    access_token = None
    
    @property
    def settings(self):
        """
        Get needed settings, API_KEY, sms gateway etc.
        """
        sms_creds = settings.TEDIX_SMS_SETTINGS
        assert (
            sms_creds and
            sms_creds.get("username") and
            sms_creds.get("username") and
            sms_creds.get('base_url')), 'SMS provider credentials are not provided!!!'
        return dict(
            username=sms_creds.get("username"),
            password=sms_creds.get('password'),
            base_url=sms_creds.get('base_url')
        )
    
    def _get(self, template, **kwargs):
        """
        GET request to SMS provider.
        Arguments:
            url (str): ready url to use
        Returns response data.
        """
        settings = kwargs.copy()
        settings.update(self.settings)
        if template != self.ACCESS_TOKEN_TEMPLATE:
            settings.update(dict(
                token=self._authorize()
            ))
        url = self._get_url_template(template).format(**settings)
        resp = requests.get(url)
        log.debug('SMS response data - "%s"', resp.content)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == STATUS_ERROR:
                if data.get('error') == ERR_100:
                    self._refresh_token()
                    return self._get(template, **kwargs)
            else:
                return data

    def _get_url_template(self, template):
        """
        Compose url with base_url and template.
        Arguments:
            template (str): One of ACCESS_TOKEN_TEMPLATE, SEND_MESSAGE_TEMPLATE, CREDIT_TEMPLATE, MESSAGE_STATUS_TEMPLATE
        Returns the url ready to use.
        """
        return urljoin(self.settings['base_url'], template)
    
    def _refresh_token(self):
        response_data = self._get(self.ACCESS_TOKEN_TEMPLATE)
        if response_data:
            log.debug('Authorize response is "%s"', response_data)
            if response_data.get('token'):
                self.access_token = response_data.get('token')
                return self.access_token
        else:
            log.warning("Failed to get access token, won't do anything")
            return

    def _authorize(self):
        """
        Get access token using credentials.
        Returns the access_token.
        """
        if self.access_token:
            return self.access_token
        return self._refresh_token()

    def send_message(self, number, message):
        """
        Send SMS to number with message.
        Arguments:
            number (int, str): Telephone number to send message
            message (str): Message to be sent.
        Returns dict of message's response data if any, otherways None
        """
        if not self.access_token:
            token = self._authorize()
            if not token:
                return
        settings = {
            'number': number,
            'message': quote_plus(quote_plus(message)), # the durty hack, didn't find another solution to handle the message
        }
        response_data = self._get(self.SEND_MESSAGE_TEMPLATE, **settings)
        if response_data:
            log.info('Send message response data - "%s"', response_data)
            return response_data
        else:
            log.error('Error while sending message')

    def get_credit(self):
        """
        Get credit.
        Returns string with credit.
        """
        response_data = self._get(self.CREDIT_TEMPLATE)
        return response_data.get('credit') if response_data else ''

    def get_sms_status(self, queue):
        """
        Get statuses of sms by queue.
        Arguments:
            queue (str): sms queue identificator
        Returns statuses of message (probably can be more than one)
        """
        status_mapping = {
            '0': 'queued',
            '1': 'sms sent',
            '2': 'failed to send',
            '3': 'sms was shipped'
        }
        response_data = self._get(self.MESSAGE_STATUS_TEMPLATE, **{'queue': queue})
        if response_data:
            data = response_data.get('data')
            queue_history = []
            for datum in data:
                status = datum.get('status')
                queue_history.append(status_mapping.get(status, ''))
            return ', '.join(queue_history)
