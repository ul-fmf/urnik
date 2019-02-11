import datetime


def teden_dneva(dan):
    ponedeljek = dan - datetime.timedelta(days=dan.weekday())
    nedelja = ponedeljek + datetime.timedelta(days=6)
    return (ponedeljek, nedelja)
