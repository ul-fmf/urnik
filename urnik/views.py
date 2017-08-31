from django.shortcuts import render
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
