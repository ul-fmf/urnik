from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlencode
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *


def zacetna_stran(request):
    smeri = {}
    osebe = Oseba.objects.aktivni()
    ucilnice = Ucilnica.objects.objavljene()
    return render(request, 'zacetna_stran.html', {
        'stolpci_smeri': [
            Letnik.objects.filter(oddelek=Letnik.MATEMATIKA),
            Letnik.objects.filter(oddelek=Letnik.FIZIKA),
        ],
        'osebe': sorted(osebe, key=lambda oseba: oseba.vrstni_red()),
        'ucilnice': ucilnice,
        'izbira': 'izbira' in request.GET,
    })


def urnik(request, srecanja, naslov, barve=None):
    legenda = barve
    if barve is None:
        barve = Predmet.objects.filter(srecanja__in=srecanja).distinct()
    if request.user.is_authenticated and request.session.get('urejanje', False):
        if request.META['QUERY_STRING']:
            next_url = '{}?{}'.format(request.path, request.META['QUERY_STRING'])
        else:
            next_url = request.path
        return render(request, 'urnik.html', {
            'nacin': 'urejanje',
            'naslov': naslov,
            'srecanja': srecanja.urnik(barve=barve),
            'odlozena_srecanja': Srecanje.objects.odlozena(),
            'prekrivanja_po_tipih': Srecanje.objects.prekrivanja(),
            'next': next_url,
            'barve': barve,
        })
    else:
        return render(request, 'urnik.html', {
            'nacin': 'ogled',
            'naslov': naslov,
            'srecanja': srecanja.urnik(barve=barve),
            'barve': legenda,
        })


def urnik_osebe(request, oseba_id):
    oseba = get_object_or_404(Oseba, id=oseba_id)
    naslov = str(oseba)
    return urnik(request, oseba.vsa_srecanja(), naslov)


def urnik_letnika(request, letnik_id):
    letnik = get_object_or_404(Letnik, id=letnik_id)
    naslov = str(letnik)
    return urnik(request, letnik.srecanja().all(), naslov)


def urnik_ucilnice(request, ucilnica_id):
    ucilnica = get_object_or_404(Ucilnica, id=ucilnica_id)
    naslov = 'Učilnica {}'.format(ucilnica.oznaka)
    return urnik(request, ucilnica.srecanja.all(), naslov, barve=[])


def urnik_predmeta(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id)
    naslov = str(predmet)
    return urnik(request, predmet.srecanja.all(), naslov)


def sestavljen_urnik(request):
    letniki = Letnik.objects.filter(id__in=request.GET.getlist('letnik'))
    osebe = Oseba.objects.filter(id__in=request.GET.getlist('oseba'))
    ucilnice = Ucilnica.objects.filter(id__in=request.GET.getlist('ucilnica'))
    srecanja_letnikov = Srecanje.objects.filter(predmet__letniki__in=letniki)
    srecanja_uciteljev = Srecanje.objects.filter(ucitelj__in=osebe)
    srecanja_slusateljev = Srecanje.objects.filter(predmet__slusatelji__in=osebe)
    srecanja_ucilnic = Srecanje.objects.filter(ucilnica__in=ucilnice)
    srecanja = (srecanja_letnikov | srecanja_uciteljev |
                srecanja_slusateljev | srecanja_ucilnic).distinct()
    return urnik(request, srecanja, 'Sestavljen urnik', barve=list(letniki) + list(osebe) + list(ucilnice))


@login_required
def premakni_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    if request.method == 'POST':
        dan = int(request.POST['dan'])
        ura = int(request.POST['ura'])
        ucilnica = get_object_or_404(Ucilnica, id=request.POST['ucilnica'])
        srecanje.premakni(dan, ura, ucilnica)
        return redirect(request.POST['next'])
    else:
        return render(request, 'urnik.html', {
            'nacin': 'premikanje',
            'naslov': 'Premikanje srečanja',
            'srecanja': srecanje.povezana_srecanja().urnik(),
            'odlozena_srecanja': Srecanje.objects.odlozena(),
            'prekrivanja_po_tipih': {},
            'prosti_termini': srecanje.prosti_termini(request.GET['tip'], 'MAT' if 'matematika' in ','.join(group.name for group in request.user.groups.all()) else 'FIZ'),
            'premaknjeno_srecanje': srecanje,
            'next': request.META.get('HTTP_REFERER', reverse('zacetna_stran')),
        })


@login_required
def podvoji_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.podvoji()
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@login_required
def odlozi_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.odlozi()
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@login_required
def nastavi_trajanje_srecanja(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    trajanje = int(request.POST['trajanje'])
    srecanje.nastavi_trajanje(trajanje)
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@login_required
def preklopi_urejanje(request):
    request.session['urejanje'] = not request.session.get('urejanje', False)
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))
