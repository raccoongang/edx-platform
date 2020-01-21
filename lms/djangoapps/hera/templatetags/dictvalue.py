from django import template
from urllib import quote_plus

register = template.Library()

@register.assignment_tag
def dictvalue(answers, key):
    """Function accepts dictionary and key return value."""

    for answer in answers:
        if answer['name'] == key:
            return answer['value']
    return ''
