import json
from django.conf import settings
from django.core.urlresolvers import reverse
from edxmako.shortcuts import render_to_string
from shoppingcart.processors.helpers import get_processor_config
from shoppingcart.models import Order
from mpesa_api.tasks import check_paymet
import logging

log = logging.getLogger(__name__)


def render_purchase_form_html(cart, callback_url=''):
    return render_to_string('shoppingcart/mpesa_form.html', {
        'action': get_processor_config().get('PURCHASE_ENDPOINT'),
        'params': {
            'cmd': '_xclick',
            'charset': 'utf-8',
            'currency_code': cart.currency.upper(),
            'amount': cart.total_cost,
            'item_name': "Camara:{}".format(cart.total_cost),
            'custom': cart.id,
            'business': get_processor_config().get('CLIENT_ID'),
            'notify_url': callback_url,
            'cancel_return': 'https://{}{}'.format(settings.SITE_NAME, reverse('shoppingcart.views.show_cart')),
            'return': 'https://{}{}'.format(settings.SITE_NAME, reverse('dashboard')),
        }
    })


def process_postpay_callback(params):
    mpesa_result = check_paymet(int(params['order_id']))
    order = Order.objects.get(id=int(mpesa_result['custom']))
    if mpesa_result['payment_status'] == 'ok':
        log.info('Order "{}" and transaction "{}" is successed'.format(order, mpesa_result['txn_id']))
        order.purchase(
            processor_reply_dump=json.dumps(params)
        )
        return {'success': True, 'order': order, 'error_html': ''}
    else:
        log.error('Order "{}" and transaction "{}" is failed'.format(order, mpesa_result['txn_id']))
        return {'success': False, 'order': order, 'error_html': 'Transaction "{}" is filed'.format(mpesa_result['txn_id'])}

def get_purchase_endpoint():
    """
    Return the URL of the payment end-point for CyberSource.

    Returns:
        unicode
    """
    return get_processor_config().get('PURCHASE_ENDPOINT', '')

def get_signed_purchase_params(cart, callback_url=None, extra_data=None):
    """
    This method will return a digitally signed set of CyberSource parameters

    Args:
        cart (Order): The order model representing items in the user's cart.

    Keyword Args:
        callback_url (unicode): The URL that CyberSource should POST to when the user
            completes a purchase.  If not provided, then CyberSource will use
            the URL provided by the administrator of the account
            (CyberSource config, not LMS config).

        extra_data (list): Additional data to include as merchant-defined data fields.

    Returns:
        dict
    """
    total_cost = cart.total_cost
    amount = "{0:0.2f}".format(total_cost)
    params = OrderedDict()
    #TODO: add all params for Mpesa API
    return params
