from urnik.models import Oseba, Ucilnica, Letnik, Predmet
from . import views


def search_data(request):
    return {
        'letniki_search': Letnik.objects.filter(oddelek__in=[Letnik.FIZIKA, Letnik.MATEMATIKA]),
        'osebe_search': sorted(Oseba.objects.aktivni()),
        'ucilnice_search': sorted(Ucilnica.objects.objavljene()),
        'predmeti_search': sorted(Predmet.objects.exclude(ime="")),
    }

def izbrani_semester(request):
    return {
        'izbrani_semester': views.izbrani_semester(request),
        'ogled_starega_semestra': views.ogled_starega_semestra(request),
        'izbrani_semester_id': views.izbrani_semester_id(request),
    }
