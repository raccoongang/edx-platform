import json
from django.conf import settings
from django.core.urlresolvers import reverse
from edxmako.shortcuts import render_to_string
from shoppingcart.processors.helpers import get_processor_config
from shoppingcart.models import Order

import logging

log = logging.getLogger(__name__)


def render_purchase_form_html(cart, callback_url=''):
    from shoppingcart.views import verify_for_closed_enrollment
    shoppingcart_items = verify_for_closed_enrollment(cart.user, cart)[-1]
    description = [("Payment for course '{}'\n".format(course.display_name)) for item, course in shoppingcart_items]
    return render_to_string('shoppingcart/flutterwave_form.html', {
        'API_URL': get_processor_config().get('API_URL'),
        'PBFPubKey': get_processor_config().get('PUBLIC_KEY'),
        'success_url': reverse('shoppingcart.views.show_receipt', args=[cart.id]),
        'params': {
            'customer_email': cart.user.email,
            'amount': cart.total_cost,
            'currency': cart.currency.upper(),
            'txref': cart.id,
            'cancel_return': 'http://{}{}'.format(settings.SITE_NAME, reverse('shoppingcart.views.show_cart')),
            'return': 'http://{}{}'.format(settings.SITE_NAME, reverse('dashboard')),
        }
    })


def process_postpay_callback(params):
    order = Order.objects.filter(id=int(params['txRef'])).first()
    verification_hash = get_processor_config().get('VERIFICATION_HASH')

    if order is None:
        return {
            'success': False,
            'order': None,
            'error_html': 'Order with id "{}" doesn\'t exist'.format(params['txRef']),
        }

    if params['verification_hash'] != verification_hash:
        return {
            'success': False,
            'order': None,
            'error_html': 'Verification hash is wrong',
        }

    if params['status'] == 'successful':
        log.info('Order "%s" is succeeded', params['txRef'])
        order.purchase(
            ccnum='****{}'.format(params['entity[card_last4]']),
            processor_reply_dump=json.dumps(params),
        )
        return {'success': True, 'order': order, 'error_html': ''}
    else:
        log.error('Order "%s" is failed', params['txRef'])
        return {
            'success': False,
            'order': order,
            'error_html': 'Order "{}" is failed'.format(params['txRef']),
        }
