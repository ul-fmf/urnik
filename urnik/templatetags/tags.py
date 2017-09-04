from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag()
def dnevi():
    DNEVI = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
    enota_sirine = 1 / len(DNEVI)
    return mark_safe('<div id="dnevi">' + ''.join('''
            <div class="dan" style="left: {:.2%}">
            {}
        </div>
        '''.format(indeks_dneva / len(DNEVI), ime_dneva)
        for indeks_dneva, ime_dneva in enumerate(DNEVI)) + '</div>')

@register.simple_tag()
def ure():
    min_ura, max_ura = 7, 20
    enota_visine = 1 / (max_ura - min_ura)
    return mark_safe('<div id="ure">' + ''.join('''
            <div class="ura" style="bottom: {:.2%}">
            <span>{}</span>
        </div>
        '''.format((max_ura - ura) * enota_visine, ura if ura >= min_ura else '')
        for ura in range(min_ura, max_ura)) + '</div>')
