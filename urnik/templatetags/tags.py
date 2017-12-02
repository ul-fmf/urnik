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

BARVE = [
    'rgba(255, 81, 54, 0.5)',
    'rgba(64, 192, 192, 0.5)',
    'rgba(255, 138, 47, 0.5)',
    'rgba(92, 128, 0, 0.5)',
    'rgba(106, 71, 148, 0.42)',
    'rgba(255, 143, 145, 0.5)',
    'rgba(31,120,180, 0.5)',
    'rgba(248, 255, 64, 0.5)',
    'rgba(177,89,40, 0.5)',
]

@register.simple_tag()
def pobarvaj(barva):
    return "background: {}".format(BARVE[barva % len(BARVE)])

@register.simple_tag()
def pobarvajvec(barve):
    if barve:
        barve = ', '.join(
            ('{0} {1:.2%}, {0} {2:.2%}'.format(BARVE[barva % len(BARVE)], i / len(barve), (i + 1) / len(barve))
                for i, barva in enumerate(barve)))
        return "background: repeating-linear-gradient(135deg, {});".format(barve)
    return ''
