import json
import logging
from django.core.urlresolvers import reverse
import paypalrestsdk

from django.conf import settings
from django.utils.translation import ugettext as _
from edxmako.shortcuts import render_to_string
from microsite_configuration import microsite
from shoppingcart.models import Order
from shoppingcart.processors.exceptions import CCProcessorDataException
from shoppingcart.processors.helpers import get_processor_config


log = logging.getLogger(__name__)


def init_paypalrestsdk():
    """
    Initialize paypal REST SDK.
    """
    paypal_configuration = get_processor_config()
    # Initialize the PayPal REST SDK
    paypalrestsdk.configure({
        'mode': paypal_configuration['MODE'],
        'client_id': paypal_configuration['CLIENT_ID'],
        'client_secret': paypal_configuration['CLIENT_SECRET']
    })

init_paypalrestsdk()


def render_purchase_form_html(cart, callback_url=None, extra_data=None):
    """
    Render a purchase form.
    """
    return render_to_string('shoppingcart/cybersource_form.html', {
        'action': reverse("shoppingcart.views.paypal_create"),
        'params': {}
    })


def process_postpay_callback(params):
    """
    Process payment callback.
    """
    payment_support_email = microsite.get_value('payment_support_email', settings.PAYMENT_SUPPORT_EMAIL)
    payer_id = params.get('PayerID')
    payment_id = params.get('paymentId')

    if payment_id:
        payment = paypalrestsdk.Payment.find(payment_id)
        data = payment.to_dict()
        if payment.execute({"payer_id": payer_id}):
            log.info('Payment execute. Params: {} data: {}'.format(json.dumps(params), json.dumps(data)))
            transactions = data.get('transactions', [])
            if len(transactions):
                order_id = transactions[0].get('invoice_number', -1)

                try:
                    order = Order.objects.get(id=int(order_id))
                except Order.DoesNotExist:
                    log.info('No a purchase. Params: {}'.format(json.dumps(params)))
                    raise CCProcessorDataException(_("The payment processor accepted an order whose number is not in our system."))

                _record_purchase(data, order)
                return {
                    'success': True,
                    'order': order,
                    'error_html': ''
                }

        error_html = _format_error_html(
            _(
                u"Sorry! Our payment processor sent us back a payment confirmation that had inconsistent data! "
                u"We apologize that we cannot verify whether the charge went through and take further action on your order. "
                u"The specific error message is: {msg} "
                u"Your credit card may possibly have been charged. Contact us with payment-specific questions at {email}."
            ).format(
                msg=u'<span class="exception_msg">{msg}</span>'.format(msg=payment.error['message']),
                email=payment_support_email
            )
        )

    else:
        error_html = _format_error_html(
            _(
                u"Sorry! Our payment processor sent us back a message saying that you have cancelled this transaction. "
                u"The items in your shopping cart will exist for future purchase. "
                u"If you feel that this is in error, please contact us with payment-specific questions at {email}."
            ).format(
                email=payment_support_email
            )
        )
    log.info('No a purchase - {}'.format(json.dumps(params)))
    return {
        'success': False,
        'order': None,
        'error_html': error_html
    }


def _record_purchase(params, order):
    """
    Save purchase order to DB.
    """
    # Mark the order as purchased and store the billing information
    payer = params.get('payer', {})
    payer_info = payer.get('payer_info', {})
    # Data was formerly present under 'billing_address', but now it seems to be at 'shipping_address'
    billing_address = payer_info.get('billing_address') or payer_info.get('shipping_address', {})
    order.purchase(
        first=payer_info.get('first_name', ''),
        last=payer_info.get('last_name', ''),
        street1=billing_address.get('line1', ''),
        street2=billing_address.get('line2', ''),
        city=billing_address.get('city', ''),
        state=billing_address.get('state', ''),
        country=billing_address.get('country_code', ''),
        postalcode=billing_address.get('postal_code', ''),
        processor_reply_dump=json.dumps(params)
    )


def _format_error_html(msg):
    """
    Format an HTML error message.
    """
    return u'<p class="error_msg">{msg}</p>'.format(msg=msg)
