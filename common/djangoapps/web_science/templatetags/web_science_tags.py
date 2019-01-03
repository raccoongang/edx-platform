from django import template
from django.db.models.query_utils import Q
from django.template import Context

from web_science.models import WebScienceCourseOverview

register = template.Library()


@register.simple_tag(takes_context=True)
def web_science_generate_css(context):
    result = ''
    css_template = context.template.engine.get_template('web_science/courses.css.html')
    for web_science in WebScienceCourseOverview.objects.filter(Q(color__isnull=False) | Q(image__isnull=False)):
        result += css_template.render(Context({
            'web_science': web_science,
        }))
    return result
