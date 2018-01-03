from urnik.models import Oseba, Ucilnica, Letnik


def search_data(request):
    return {
        'letniki_search': Letnik.objects.filter(oddelek__in=[Letnik.FIZIKA, Letnik.MATEMATIKA]),
        'osebe_search': sorted(Oseba.objects.aktivni(), key=lambda oseba: oseba.vrstni_red()),
        'ucilnice_search': Ucilnica.objects.objavljene(),
    }