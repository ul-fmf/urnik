from django.shortcuts import get_object_or_404, render
from .models import *


def zacetna_stran(request):
    smeri = {}
    for letnik in Letnik.objects.all():
        try:
            smer, opis = str(letnik).split(',')
            letnik.opis = opis
            smeri.setdefault(smer, []).append(letnik)
        except:
            pass
    osebe = Oseba.objects.aktivni().exclude(priimek='X')
    ucilnice = Ucilnica.objects.filter(vidna=True).exclude(oznaka='X')
    stolpci_smeri = ([], [])
    for i, (smer, letniki) in enumerate(sorted(smeri.items())):
        stolpci_smeri[i % 2].append({
            'ime': smer,
            'letniki': letniki
        })
    return render(request, 'zacetna_stran.html', {
        'stolpci_smeri': stolpci_smeri,
        'osebe': osebe,
        'ucilnice': ucilnice,
    })


def urnik(request, srecanja, naslov):
    raise Exception('Urnik za {} še ni narejen'.format(naslov))


def urnik_osebe(request, oseba_id):
    oseba = get_object_or_404(Oseba, id=oseba_id)
    return urnik(request, oseba.srecanja.all(), oseba)


def urnik_letnika(request, letnik_id):
    letnik = get_object_or_404(Letnik, id=letnik_id)
    return urnik(request, letnik.srecanja().all(), letnik)


def urnik_ucilnice(request, ucilnica_id):
    ucilnica = get_object_or_404(Ucilnica, id=ucilnica_id)
    naslov = 'Učilnica {}'.format(ucilnica.oznaka)
    return urnik(request, ucilnica.srecanja.all(), naslov)


def urnik_predmeta(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id)
    return urnik(request, predmet.srecanja.all(), predmet)
