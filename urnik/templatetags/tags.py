from django.http import HttpResponse
from bottle import SimpleTemplate
from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.simple_tag(takes_context=True)
def render_bottle(context, name):
    kwargs = {}
    for d in context:
        kwargs.update(d)
    template = SimpleTemplate(
        name=name,
        lookup=['urnik/static/', 'urnik/templates/']
    )
    return mark_safe(template.render(**kwargs))
