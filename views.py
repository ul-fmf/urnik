from bottle import route, run, template, get, post, request, redirect, default_app
import bottle
import modeli


##########################################################################
# UREJANJE SREČANJ
##########################################################################


@get('/uredi/srecanje/<srecanje:int>/premakni/')
def premakni_srecanje(srecanje):
    return template(
        'urnik',
        nacin='premikanje',
        premaknjeno_srecanje=modeli.podatki_srecanja(srecanje),
        odlozena_srecanja=modeli.odlozena_srecanja(),
        srecanja=modeli.povezana_srecanja(srecanje),
        prosti_termini=modeli.prosti_termini(srecanje),
        next=request.headers.get('referer') or '/uredi/',
        prekrivanja={},
    )


@post('/uredi/srecanje/<srecanje:int>/premakni/')
def premakni_srecanje(srecanje):
    dan = int(request.forms.dan)
    ura = int(request.forms.ura)
    ucilnica = int(request.forms.ucilnica)
    modeli.premakni_srecanje(srecanje, dan, ura, ucilnica)
    redirect(request.forms.next)


@post('/uredi/srecanje/<srecanje:int>/izbrisi/')
def izbrisi(srecanje):
    modeli.pobrisi_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/uredi/')


@post('/uredi/srecanje/<srecanje:int>/podvoji/')
def podvoji(srecanje):
    modeli.podvoji_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/uredi/')

@post('/uredi/srecanje/<srecanje:int>/odlozi/')
def odlozi(srecanje):
    modeli.odlozi_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/uredi/')


@post('/uredi/srecanje/<srecanje:int>/trajanje/')
def trajanje_srecanja(srecanje):
    trajanje = int(request.forms.trajanje)
    modeli.nastavi_trajanje(srecanje, trajanje)
    redirect(request.headers.get('referer') or '/uredi/')


@get('/uredi/srecanje/<srecanje:int>/')
def uredi_srecanje(srecanje):
    return template(
        'uredi_srecanje',
        srecanje=modeli.podatki_srecanja(srecanje),
        ucitelji=modeli.podatki_oseb(),
        predmeti=modeli.podatki_predmetov(),
        ucilnice=modeli.podatki_ucilnic(),
        next=request.headers.get('referer') or '/uredi/',
    )


@post('/uredi/srecanje/<srecanje:int>/')
def uredi_srecanje_post(srecanje):
    modeli.shrani_srecanje({
        'id': srecanje,
        'ucitelj': int(request.forms.ucitelj),
        'ucilnica': int(request.forms.ucilnica),
        'predmet': int(request.forms.predmet),
        'tip': request.forms.tip,
        'oznaka': request.forms.oznaka if request.forms.oznaka else None,
    })
    redirect(request.forms.next)

##########################################################################
# PRIKAZ URNIKA
##########################################################################


@route('/uredi/urnik')
def urnik():
    return template(
        'urnik',
        nacin='urejanje',
        srecanja=modeli.urnik(
            letniki=[int(letnik) for letnik in request.query.getall('letnik')],
            osebe=[int(oseba) for oseba in request.query.getall('oseba')],
            predmeti=[int(predmet) for predmet in request.query.getall('predmet')],
            ucilnice=[int(ucilnica)
                      for ucilnica in request.query.getall('ucilnica')],
        ),
        odlozena_srecanja=modeli.odlozena_srecanja(),
        prekrivanja=modeli.prekrivanja(),
    )

@route('/letnik/<letnik:int>/')
def urnik(letnik):
    l = modeli.podatki_letnika(letnik)
    if l['leto']:
        naslov = '{}, {}. letnik'.format(l['smer'], l['leto'])
    else:
        naslov = l['smer']
    return template(
        'urnik',
        nacin='ogled',
        srecanja=modeli.urnik(
            letniki=[letnik],
            osebe=[],
            predmeti=[],
            ucilnice=[],
        ),
        naslov=naslov,
    )
@route('/oseba/<oseba:int>/')
def urnik(oseba):
    l = modeli.podatki_osebe(oseba)
    naslov = '{} {}'.format(l['ime'], l['priimek'])
    return template(
        'urnik',
        nacin='ogled',
        srecanja=modeli.urnik(
            letniki=[],
            osebe=[oseba],
            predmeti=[],
            ucilnice=[],
        ),
        naslov=naslov,
    )
@route('/ucilnica/<ucilnica:int>/')
def urnik(ucilnica):
    l = modeli.podatki_ucilnice(ucilnica)
    naslov = 'Učilnica {}'.format(l['oznaka'])
    return template(
        'urnik',
        nacin='ogled',
        srecanja=modeli.urnik(
            letniki=[],
            osebe=[],
            predmeti=[],
            ucilnice=[ucilnica],
        ),
        naslov=naslov,
    )
@route('/predmet/<predmet:int>/')
def urnik(predmet):
    l = modeli.podatki_predmeta(predmet)
    naslov = l['ime']
    return template(
        'urnik',
        nacin='ogled',
        srecanja=modeli.urnik(
            letniki=[],
            osebe=[],
            predmeti=[predmet],
            ucilnice=[],
        ),
        naslov=naslov,
    )

@route('/uredi/fiziki/')
def fiziki():
    return template(
        'urnik',
        nacin='urejanje',
        srecanja=modeli.fiziki(),
        odlozena_srecanja=[],
        prekrivanja={},
    )
