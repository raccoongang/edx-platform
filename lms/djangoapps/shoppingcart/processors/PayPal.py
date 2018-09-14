"""
Implementation of the PayPal credit/debit card processor using the newer "REST API".

To enable this implementation, add the following Django settings:

    CC_PROCESSOR_NAME = "PayPal"
    CC_PROCESSOR = {
        "PayPal": {
            "PAYPAL_MODE": "sandbox | live",
            "PAYPAL_CLIENT_ID": "<client_id>",
            "PAYPAL_CLIENT_SECRET": "<client_secret>"
        },

    }

"""
import re
import json
import logging
import paypalrestsdk
from collections import OrderedDict, defaultdict
from django.conf import settings
from django.utils.translation import ugettext as _
from edxmako.shortcuts import render_to_string
from shoppingcart.models import Order
from shoppingcart.processors.exceptions import CCProcessorUserDeclined, CCProcessorDataException
from shoppingcart.processors.helpers import get_processor_config
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from paypalrestsdk import Payment

log = logging.getLogger(__name__)


def paypal_configure():
    """
    Configures your PayPal Account. Necessary to create or execute any payment. Without configuring
    none payment can be  created or executed.
    """

    paypalrestsdk.configure({
        'mode': get_processor_config().get('PAYPAL_MODE', 'sandbox'),
        'client_id': get_processor_config().get('PAYPAL_CLIENT_ID', ''),
        'client_secret': get_processor_config().get('PAYPAL_CLIENT_SECRET', '')
    })


def paypal_create_payment(cart, shoppingcart_items, execute_url):
    """
    Creates Payment. Creating payment gives unique token, payment id and payer id.
    Payment Method should be either credit_card or paypal. If it is credit_card then
    credit card information should be provided else it won't create payment. To see
    how how to include credit card information visit
    https://github.com/paypal/PayPal-Python-SDK
    """

    # Fetches the necessary parameters to create payment
    params = get_purchase_params(cart, shoppingcart_items)

    # Configures your PayPal Account.
    paypal_configure()
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": execute_url,
            "cancel_url": execute_url
        },
        "transactions": [{
            "item_list": {
                "items": [data for data in params['course_details']]
            },

            "amount": {
                "total": params['amount'],
                "currency": params['currency'].upper()
            },
            "description": params['productinfo']
        }]
    })

    # Returns True if payment is executed successfully else will display proper Error Message.
    if payment.create():
        log.info("Payment[%s] created successfully" % (payment.id))
        for link in payment.links:
            if link.method == "REDIRECT":
                return {
                    'success': True,
                    'link': link.href,
                    'error_html': ''
                }
    else:
        log.exception("Error while creating payment. The error was: %s" % (payment.error))
        return {
            'success': False,
            'link': '',
            'order': '',
            'error_html': _get_processor_exception_html(payment)
        }


def paypal_execute_payment(params):
    """
    Executes the payment. For Execution requires the payment id and payer id which payment sends in GET method
    Only after Executing the payment, the payment will be completed else it will just be created which won't
    do any transaction. Once the payment is executed then payment id and payer id becomes invalid.
    """
    try:
        payer_id = params.get('PayerID', '')
        payment_id = params.get('paymentId', '')
        payment = Payment.find(payment_id)

        # Return True if payment is executed successfully.
        if payment.execute({"payer_id": payer_id}):
            log.info("Payment[%s] execute successfully" % (payment.id))
            return{
                'success': True,
            }
        else:
            log.exception("Error while executing payment. The error was: %s" % (payment.error))
            return {
                'success': False,
                'order': '',
                'error_html': _get_processor_exception_html(payment)
            }
    except Exception as error:
        log.exception("Error while executing payment")
        return {
            'success': False,
            'order': '',
            'error_html': _get_processor_exception_html(error)
        }


def render_purchase_form_html(cart, callback_url=None, create_payment_url=None, **kwargs):
    """
    Renders the HTML of the hidden POST form that must be used to initiate a purchase with PayPal
    """

    return render_to_string('shoppingcart/paypal_form.html', {
        'action': create_payment_url
    })


def get_purchase_params(cart, shoppingcart_items):
    """
    This method will build out a dictionary of parameters needed by PayPal to create the payment.

    Args:
        cart (Order): The order model representing items in the user's cart.

    Keyword Args:

        shoppingcart_items (list): Additional data to include as item name, quantity and price that needs to
        be displayed on PayPal Site.

    Returns:
        dict

    """
    total_cost = cart.total_cost
    amount = "{0:0.2f}".format(total_cost)
    params = OrderedDict()
    params['course_details'] = []
    for item, course in shoppingcart_items:
        details = {}
        details['name'] = course.display_name
        details['price'] = "{0:0.2f}".format(item.unit_cost)
        details['quantity'] = item.qty
        details['currency'] = cart.currency.upper()
        params['course_details'].append(details)
    try:
        params['productinfo'] = cart.orderitem_set.all().values()[0]['line_desc']
    except:
        params['productinfo'] = "Description Unavailable"
    params['amount'] = amount
    params['currency'] = cart.currency
    params['orderPage_transactionType'] = 'sale'
    params['orderNumber'] = "OrderId: {0:d}".format(cart.id)

    return params


def process_postpay_callback(params):
    """
    Handle a response after executing the payment.

    Concrete implementations should:
        1) Find the payment details using the payment id.
        2) If successful, mark the order as purchased and call `purchased_callbacks` of the cart items.
        3) If unsuccessful, try to figure out why and generate a helpful error message.
        4) Return a dictionary of the form:
            {'success': bool, 'order': Order, 'error_html': str}

    Args:
        params (dict): Dictionary of parameters received from the payment processor.

    Keyword Args:
        Can be used to provide additional information to concrete implementations.

    Returns:
        dict

    """
    try:
        # Find the Payment Details.
        payment = Payment.find(params['paymentId']).to_dict()

        # Fetches the Payer Info
        payment_details = payment['payer']['payer_info']
        result = _payment_accepted(
            params.get('order_id', '')
        )
        if result['accepted']:
            _record_purchase(payment_details, result['order'])
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
    except Exception as error:
        log.exception('error processing PayPal postpay callback')
        # if we have the order and the id, log it
        if hasattr(error, 'order'):
            _record_payment_info(params, error.order)
        else:
            log.info(json.dumps(params))
        return {
            'success': False,
            'order': None,  # due to exception we may not have the order
            'error_html': _get_processor_exception_html(error)
        }


def _payment_accepted(order_id):
    """
    Feteches the Order associated with the payment.

    Args:
        order_num (int): The ID of the order associated with this payment.

    Returns:
        dictionary of the form:
        {
            'accepted': bool,
            'currency': string,
            'order': Order
        }

    Raises:
        CCProcessorDataException: The order does not exist.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise CCProcessorDataException(_("The payment processor accepted an order whose number is not in our system."))

    return {
        'accepted': True,
        'currency': 'usd',
        'order': order
    }


def _record_purchase(params, order):
    """
    Record the purchase and run purchased_callbacks

    Args:
        params (dict): The parameters we received from PayPal.
        order (Order): The order associated with this payment.

    Returns:
        None

    """
    # Usually, the credit card number will have the form "xxxxxxxx1234"
    # Parse the string to retrieve the digits.
    # If we can't find any digits, use placeholder values instead.
    ccnum_str = params.get('req_card_number', '')
    first_digit = re.search(r"\d", ccnum_str)
    if first_digit:
        ccnum = ccnum_str[first_digit.start():]
    else:
        ccnum = "####"

    if settings.FEATURES.get("LOG_POSTPAY_CALLBACKS"):
        log.info(
            "Order %d purchased with params: %s", order.id, json.dumps(params)
        )

    # Fetches the shipping details.
    shipping_details = params.get('shipping_address', {})

    # Mark the order as purchased and store the billing information
    order.purchase(
        first=params.get('first_name', ''),
        last=params.get('last_name', ''),
        street1=shipping_details.get('line1', ''),
        street2=shipping_details.get('line2', ''),
        city=shipping_details.get('city', ''),
        state=shipping_details.get('state', ''),
        country=shipping_details.get('country_code', ''),
        postalcode=shipping_details.get('postal_code', ''),
        ccnum=ccnum,
        cardtype=CARDTYPE_MAP[params.get('req_card_type', '')],
        processor_reply_dump=json.dumps(params)
    )


def _record_payment_info(params, order):
    """
    Record the purchase and run purchased_callbacks

    Args:
        params (dict): The parameters we received from PayPal.

    Returns:
        None
    """
    if settings.FEATURES.get("LOG_POSTPAY_CALLBACKS"):
        log.info(
            "Order %d processed (but not completed) with params: %s", order.id, json.dumps(params)
        )

    order.processor_reply_dump = json.dumps(params)
    order.save()


def _get_processor_exception_html(exception=None):
    """
    Return HTML indicating that an error occurred.

    Args:
        exception (CCProcessorException): The exception that occurred.

    Returns:
        unicode: The rendered HTML.

    """
    payment_support_email = configuration_helpers.get_value('payment_support_email', settings.PAYMENT_SUPPORT_EMAIL)

    if isinstance(exception, CCProcessorDataException):
        return _format_error_html(
            _(
                u"Sorry! Our payment processor sent us back a payment confirmation that had inconsistent data! "
                u"We apologize that we cannot verify whether the charge went through and take further action on your order. "
                u"The specific error message is: {msg} "
                u"Your credit card may possibly have been charged.  Contact us with payment-specific questions at {email}."
            ).format(
                msg=u'<span class="exception_msg">{msg}</span>'.format(msg=exception.message),
                email=payment_support_email
            )
        )

    elif isinstance(exception, CCProcessorUserDeclined):
        return _format_error_html(
            _(
                u"We're sorry, but this payment was declined. The items in your shopping cart have been saved. "
                u"If you have any questions about this transaction, please contact us at {email}."
            ).format(
                email=payment_support_email
            )
        )
    elif isinstance(exception, paypalrestsdk.payments.Payment):
        return _format_error_html(
            _(
                u"We're sorry, but this payment was declined. The items in your shopping cart have been saved. "
                u"The error was {message}."
                u"Details: {details}."
                u"Please contact us at {email} for assistance."
            ).format(
                message=exception.error['message'],
                details=exception.error['details'],
                email=payment_support_email
            )
        )
    else:
        return _format_error_html(
            _(
                u" Sorry! Your payment could not be processed because an unexpected exception occurred. "
                u"Please contact us at {email} for assistance."
            ).format(email=payment_support_email)
        )


def _format_error_html(msg):
    """ Format an HTML error message """
    return u'<p class="error_msg">{msg}</p>'.format(msg=msg)


CARDTYPE_MAP = defaultdict(lambda: "UNKNOWN")
CARDTYPE_MAP.update(
    {
        '001': 'Visa',
        '002': 'MasterCard',
        '003': 'American Express',
        '004': 'Discover',
        '005': 'Diners Club',
        '006': 'Carte Blanche',
        '007': 'JCB',
        '014': 'EnRoute',
        '021': 'JAL',
        '024': 'Maestro',
        '031': 'Delta',
        '033': 'Visa Electron',
        '034': 'Dankort',
        '035': 'Laser',
        '036': 'Carte Bleue',
        '037': 'Carta Si',
        '042': 'Maestro Int.',
        '043': 'GE Money UK card'
    }
)
