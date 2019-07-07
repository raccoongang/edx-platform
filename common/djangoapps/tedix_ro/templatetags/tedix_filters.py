from django import template

register = template.Library()


@register.filter
def get_errors_value(data, key_name):
    form_fields_map = {
        'city': 'school_city',
        'teacher_email': 'instructor',
        'public_name': 'name'
    }
    return data.get(form_fields_map.get(key_name, key_name), '')
