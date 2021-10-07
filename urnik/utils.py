import datetime

from django.utils.dateparse import parse_date


def teden_dneva(dan):
    ponedeljek = dan - datetime.timedelta(days=dan.weekday())
    nedelja = ponedeljek + datetime.timedelta(days=6)
    return (ponedeljek, nedelja)


def normaliziraj_teden(dan):
    """Vrne ponedeljek "aktivnega" tedna za `dan`.

    Če je `dan` delavnik, je to dan trenutnega tedna, če pa je sobota ali nedelja, je to ponedeljek naslednjega tedna.
    """
    try:
        dan = parse_date(dan)
        weekday = dan.weekday()
        if weekday <= 4:
            dan -= datetime.timedelta(days=weekday)
        else:
            dan += datetime.timedelta(days=7 - weekday)
    except:
        return None
    return dan
