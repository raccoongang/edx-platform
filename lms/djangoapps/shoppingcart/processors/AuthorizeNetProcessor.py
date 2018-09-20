"""
AuthorizeNet Accept Hosted Form payment processor


IMPORTANT!!
In manage.py comment this lines:

#from safe_lxml import defuse_xml_libs
#defuse_xml_libs()

with uncommented code you you'll
get an import error lxml.objectify from authorizenet module


Configuration:

FEATURES['ENABLE_PAYMENT_FAKE'] = False

CC_PROCESSOR_NAME = 'AuthorizeNetProcessor'
CC_PROCESSOR = {
    'AuthorizeNetProcessor': {
        'TEST_MODE': False,
        'API_LOGIN_ID': '1239qK3nK7',
        'TRANSACTION_KEY': '432hf54GchuYJ349Na',
    }
}

"""
import json
import logging
from urlparse import urljoin

import re
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import getHostedPaymentPageController, getTransactionDetailsController
from authorizenet.constants import constants
from django.conf import settings
from django.templatetags.static import static

from edxmako.shortcuts import render_to_string
from shoppingcart.models import Order, OrderItem
from shoppingcart.processors.exceptions import CCProcessorDataException, CCProcessorWrongAmountException, \
    CCProcessorException
from shoppingcart.processors.helpers import get_processor_config
from django.utils.translation import ugettext as _
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

log = logging.getLogger(__name__)

ORDER_PREFIX = 'A001'

RESPONSE_CODES = (
    (1, 'Approved'),
    (2, 'Declined'),
    (3, 'Error'),
    (4, 'Held for Review'),
)


def get_merchant_auth():
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = get_processor_config()['API_LOGIN_ID']
    merchantAuth.transactionKey = get_processor_config()['TRANSACTION_KEY']
    return merchantAuth


def render_purchase_form_html(cart, callback_url=None, extra_data=None):
    # don't render cart without items
    if not cart.has_items():
        return None

    test_mode = get_processor_config().get('TEST_MODE', False)
    payment_url = 'https://{}.authorize.net/payment/payment'.format('test' if test_mode else 'accept')

    settings = apicontractsv1.ArrayOfSetting()

    def add_settings(name, value):
        setting = apicontractsv1.settingType()
        setting.settingName = getattr(apicontractsv1.settingNameEnum, name)
        setting.settingValue = json.dumps(value)
        settings.setting.append(setting)

    add_settings('hostedPaymentBillingAddressOptions', {
        'show': True,
        'required': True
    })
    add_settings('hostedPaymentIFrameCommunicatorUrl', {
        'url': urljoin(callback_url, static('IFrameCommunicator.html')),
    })
    add_settings('hostedPaymentReturnOptions', {
        'showReceipt': False,
        'cancelUrl': urljoin(callback_url, static('IFrameCommunicator.html')),
    })

    add_settings('hostedPaymentPaymentOptions', {
        'cardCodeRequired': True,
        'showCreditCard': True,
        'showBankAccount': False,
    })

    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = 'authCaptureTransaction'
    transactionrequest.amount = cart.total_cost

    items = OrderItem.objects.filter(order=cart.id).select_subclasses()
    if len(items) == 1:
        transactionrequest.description = items[0].line_desc
    else:
        line_items = apicontractsv1.ArrayOfLineItem()
        for item in items:
            line_item = apicontractsv1.lineItemType()
            line_item.itemId = 'ITEM{}'.format(item.id)
            line_item.name = 'item'
            line_item.description = item.line_desc
            line_item.quantity = '{}'.format(item.qty)
            line_item.unitPrice = '{}'.format(item.unit_cost)
            line_items.lineItem.append(line_item)
        transactionrequest.lineItems = line_items

    order = apicontractsv1.orderType()
    order.invoiceNumber = '{}{:05}'.format(ORDER_PREFIX, cart.id)
    transactionrequest.order = order

    paymentPageRequest = apicontractsv1.getHostedPaymentPageRequest()
    paymentPageRequest.merchantAuthentication = get_merchant_auth()
    paymentPageRequest.transactionRequest = transactionrequest
    paymentPageRequest.hostedPaymentSettings = settings

    paymentPageController = getHostedPaymentPageController(paymentPageRequest)
    paymentPageController.setenvironment(constants.SANDBOX if test_mode else constants.PRODUCTION)
    paymentPageController.execute()
    paymentPageResponse = paymentPageController.getresponse()

    return render_to_string('shoppingcart/authorize_net/purchase_form.html', {
        'action': payment_url,
        'token': paymentPageResponse.token,
        'callback_url': callback_url,
    })


def process_postpay_callback(params, **kwargs):
    result = {
        'order_id': int(params['orderInvoiceNumber'][len(ORDER_PREFIX):]),
        'auth_amount': float(params['totalAmount']),
        'currency': 'USD',
        'decision': int(params['responseCode']),
        'card_number': params['accountNumber'],
        'processor_reply_dump': json.dumps(params),
        'card_type': params.get('accountType', ''),
    }

    try:
        result = _payment_accepted(
            result['order_id'],
            result['auth_amount'],
            result['currency'],
            result['decision'],
        )
        if result['accepted']:
            _record_purchase(params, result['order'])
            return {
                'success': True,
                'order': result['order'],
                'error_html': ''
            }
        else:
            _record_payment_info(params, result['order'])
            return {
                'success': False,
                'order': result['order'],
                'error_html': _get_processor_decline_html(params)
            }
    except CCProcessorException as error:
        log.exception('error processing AuthorizeNet postpay callback')
        # if we have the order and the id, log it
        if hasattr(error, 'order'):
            _record_payment_info(params, error.order)
        else:
            log.info(json.dumps(params))
        payment_support_email = configuration_helpers.get_value('payment_support_email', settings.PAYMENT_SUPPORT_EMAIL)
        return {
            'success': False,
            'order': None,  # due to exception we may not have the order
            'error_html': _(
                u"Sorry! Your payment could not be processed because an unexpected exception occurred. "
                u"Please contact us at {email} for assistance."
            ).format(email=payment_support_email)
        }


def _record_payment_info(params, order):
    """
    Record the purchase and run purchased_callbacks

    Args:
        params (dict): The parameters we received from AuthorizeNet.

    Returns:
        None
    """
    if settings.FEATURES.get("LOG_POSTPAY_CALLBACKS"):
        log.info(
            "Order %d processed (but not completed) with params: %s", order.id, json.dumps(params)
        )

    order.processor_reply_dump = json.dumps(params)
    order.save()


def _record_purchase(params, order):
    """
    Record the purchase and run purchased_callbacks

    Args:
        params (dict): The parameters we received from AuthorizeNet.
        order (Order): The order associated with this payment.

    Returns:
        None

    """
    # Usually, the credit card number will have the form "xxxxxxxx1234"
    # Parse the string to retrieve the digits.
    # If we can't find any digits, use placeholder values instead.
    ccnum_str = params.get('card_number', 'xxxx')
    ccnum = '{}{}'.format('####', ccnum_str[-4:])

    if 'transId' in params:
        transactionDetailsRequest = apicontractsv1.getTransactionDetailsRequest()
        transactionDetailsRequest.merchantAuthentication = get_merchant_auth()
        transactionDetailsRequest.transId = params['transId']
        transactionDetailsController = getTransactionDetailsController(transactionDetailsRequest)
        transactionDetailsController.execute()
        response = transactionDetailsController.getresponse()
        if str(response.messages.resultCode).lower() == 'ok' and hasattr(response.transaction, 'billTo'):
            bt = response.transaction.billTo
            params.update({
                'bill_first_name': str(getattr(bt, 'firstName', '')),
                'bill_last_name': str(getattr(bt, 'lastName', '')),
                'bill_address_line1': str(getattr(bt, 'address', '')),
                'bill_city': str(getattr(bt, 'city', '')),
                'bill_state': str(getattr(bt, 'state', '')),
                'bill_country': str(getattr(bt, 'country', '')),
                'bill_postal_code': str(getattr(bt, 'zip', '')),
            })

    if settings.FEATURES.get("LOG_POSTPAY_CALLBACKS"):
        log.info(
            "Order %d purchased with params: %s", order.id, json.dumps(params)
        )

    # Mark the order as purchased and store the billing information
    order.purchase(
        first=params.get('bill_first_name', ''),
        last=params.get('bill_last_name', ''),
        street1=params.get('bill_address_line1', ''),
        street2=params.get('bill_address_line2', ''),
        city=params.get('bill_city', ''),
        state=params.get('bill_state', ''),
        country=params.get('bill_country', ''),
        postalcode=params.get('bill_postal_code', ''),
        ccnum=ccnum,
        cardtype=params.get('card_type', ''),
        processor_reply_dump=json.dumps(params)
    )


def _payment_accepted(order_id, auth_amount, currency, decision):
    """
    Check that AuthorizeNet has accepted the payment.

    Args:
        order_num (int): The ID of the order associated with this payment.
        auth_amount (Decimal): The amount the user paid using AuthorizeNet.
        currency (str): The currency code of the payment.
        decision (str): "ACCEPT" if the payment was accepted.

    Returns:
        dictionary of the form:
        {
            'accepted': bool,
            'amt_charged': int,
            'currency': string,
            'order': Order
        }

    Raises:
        CCProcessorDataException: The order does not exist.
        CCProcessorWrongAmountException: The user did not pay the correct amount.

    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise CCProcessorDataException(_("The payment processor accepted an order whose number is not in our system."))

    if dict(RESPONSE_CODES)[decision] == 'Approved':
        if float(auth_amount) == float(order.total_cost) and currency.lower() == order.currency.lower():
            return {
                'accepted': True,
                'amt_charged': auth_amount,
                'currency': currency,
                'order': order
            }
        else:
            ex = CCProcessorWrongAmountException(
                _(
                    u"The amount charged by the processor {charged_amount} {charged_amount_currency} is different "
                    u"than the total cost of the order {total_cost} {total_cost_currency}."
                ).format(
                    charged_amount=auth_amount,
                    charged_amount_currency=currency,
                    total_cost=order.total_cost,
                    total_cost_currency=order.currency
                )
            )

            ex.order = order
            raise ex
    else:
        return {
            'accepted': False,
            'amt_charged': 0,
            'currency': 'usd',
            'order': order
        }


def _get_processor_decline_html(params):
    """
    Return HTML indicating that the user's payment was declined.

    Args:
        params (dict): Parameters we received from AuthorizeNet.

    Returns:
        unicode: The rendered HTML.

    """
    payment_support_email = configuration_helpers.get_value('payment_support_email', settings.PAYMENT_SUPPORT_EMAIL)
    return (
        _(
            "Sorry! Our payment processor did not accept your payment.  "
            "The decision they returned was {decision}, "
            "and the reason was {reason}.  "
            "You were not charged. Please try a different form of payment.  "
            "Contact us with payment-related questions at {email}."
        ).format(
            decision='<span class="decision">{decision}</span>'.format(decision=params['decision']),
            reason='<span class="reason">{reason_code}:{reason_msg}</span>'.format(
                reason_code=params['reason_code'],
                reason_msg=params['reason_message'],
            ),
            email=payment_support_email
        ),
    )
