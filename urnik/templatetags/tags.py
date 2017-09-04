from django import template
from django.utils.safestring import mark_safe
from urnik import models

register = template.Library()


@register.simple_tag()
def dnevi():
    return mark_safe('<div id="dnevi">' + ''.join('''
            <div class="dan" style="left: {:.2%}">
            {}
        </div>
        '''.format(indeks_dneva / len(models.DNEVI), ime_dneva)
        for indeks_dneva, ime_dneva in enumerate(models.DNEVI)) + '</div>')

@register.simple_tag()
def ure():
    return mark_safe('<div id="ure">' + ''.join('''
            <div class="ura" style="bottom: {:.2%}">
            <span>{}</span>
        </div>
        '''.format((models.MAX_URA - ura) * models.ENOTA_VISINE, ura if ura >= models.MIN_URA else '')
        for ura in range(models.MIN_URA, models.MAX_URA)) + '</div>')
