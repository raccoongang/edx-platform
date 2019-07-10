from django import template
from tedix_ro.forms import FORM_FIELDS_MAP

register = template.Library()


@register.filter
def get_errors_value(data, key_name):
    return data.get(FORM_FIELDS_MAP.get(key_name, key_name), '')


@register.filter
def get_item(data, key_name):
    return data.get(key_name, '')


@register.simple_tag
def get_color(state):
    state_color_map = {
        'new': '#a0cca0',
        'skipped': '#d2d2d2',
        'updated': '#f7f7a3',
        'error': '#e29898'
    }
    
    return state_color_map[state]
