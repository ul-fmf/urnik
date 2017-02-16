from bottle import route, run, template, get, post, request, redirect, default_app
import bottle
import modeli


##########################################################################
# DOMAČA STRAN
##########################################################################

@route('/')
def domaca_stran():
    return template(
        'domaca_stran',
        letniki=modeli.podatki_letnikov(),
        osebe=modeli.podatki_oseb(),
        ucilnice=modeli.podatki_ucilnic(),
        predmeti=modeli.podatki_predmetov(),
    )

##########################################################################
# UREJANJE
##########################################################################


@get('/letnik/<letnik:int>/uredi')
def uredi_letnik(letnik):
    return template(
        'uredi_letnik',
        letnik=modeli.podatki_letnika(letnik)
    )


@post('/letnik/<letnik:int>/uredi')
def uredi_letnik_post(letnik):
    modeli.shrani_letnik({
        'id': letnik,
        'smer': request.forms.smer,
        'leto': int(request.forms.leto) if requests.forms.leto else None,
    })
    redirect('/')


@get('/oseba/<oseba:int>/uredi')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.podatki_osebe(oseba)
    )


@post('/oseba/<oseba:int>/uredi')
def uredi_osebo_post(oseba):
    modeli.shrani_osebo({
        'id': oseba,
        'ime': request.forms.ime,
        'priimek': request.forms.priimek,
        'email': request.forms.email if request.forms.email else None,
    })
    redirect('/')


@get('/ucilnica/<ucilnica:int>/uredi')
def uredi_ucilnico(ucilnica):
    return template(
        'uredi_ucilnico',
        ucilnica=modeli.podatki_ucilnice(ucilnica)
    )


@post('/ucilnica/<ucilnica:int>/uredi')
def uredi_ucilnico_post(ucilnica):
    modeli.shrani_ucilnico({
        'id': ucilnica,
        'oznaka': request.forms.oznaka,
        'velikost': int(request.forms.velikost) if request.forms.velikost else None,
        'racunalniska': bool(request.forms.racunalniska),
        'skrita': bool(request.forms.skrita),
    })
    redirect('/')


@get('/predmet/<predmet:int>/uredi')
def uredi_predmet(predmet):
    return template(
        'uredi_predmet',
        predmet=modeli.podatki_predmeta(predmet),
        letniki=modeli.podatki_letnikov(),
        slusatelji=modeli.podatki_oseb(),
    )


@post('/predmet/<predmet:int>/uredi')
def uredi_predmet_post(predmet):
    ime = request.forms.ime
    kratica = request.forms.kratica
    stevilo_studentov = None if request.forms.stevilo_studentov is '' else int(request.forms.stevilo_studentov)
    letniki = [int(letnik) for letnik in request.forms.getall('letniki')]
    slusatelji = [int(slusatelj) for slusatelj in request.forms.getall('slusatelji')]
    modeli.uredi_predmet(predmet, ime, kratica, stevilo_studentov, letniki, slusatelji)
    redirect('/')

##########################################################################
# USTVARJANJE
##########################################################################


@get('/letnik/ustvari')
def ustvari_letnik():
    return template(
        'uredi_letnik'
    )


@post('/letnik/ustvari')
def ustvari_letnik_post():
    modeli.shrani_letnik({
        'smer': request.forms.smer,
        'leto': int(request.forms.leto),
    })
    redirect('/')


@get('/oseba/ustvari')
def ustvari_osebo():
    return template(
        'uredi_osebo'
    )


@post('/oseba/ustvari')
def ustvari_osebo_post():
    modeli.shrani_osebo({
        'ime': request.forms.ime,
        'priimek': request.forms.priimek,
        'email': request.forms.email if request.forms.email else None,
    })
    redirect('/')


@get('/ucilnica/ustvari')
def ustvari_ucilnico():
    return template(
        'uredi_ucilnico'
    )


@post('/ucilnica/ustvari')
def ustvari_ucilnico_post():
    modeli.shrani_ucilnico({
        'oznaka': request.forms.oznaka,
        'velikost': int(request.forms.velikost) if request.forms.velikost else None,
        'racunalniska': bool(request.forms.racunalniska),
        'skrita': bool(request.forms.skrita),
    })
    redirect('/')


@get('/predmet/ustvari')
def ustvari_predmet():
    return template(
        'uredi_predmet',
        letniki=modeli.podatki_letnikov()
    )


@post('/predmet/ustvari')
def ustvari_predmet_post():
    ime = request.forms.ime
    kratica = request.forms.kratica
    stevilo_studentov = None if request.forms.stevilo_studentov is '' else int(request.forms.stevilo_studentov)
    letniki = [int(letnik) for letnik in request.forms.getall('letniki')]
    modeli.ustvari_predmet(ime, kratica, stevilo_studentov, letniki)
    redirect('/')


##########################################################################
# UREJANJE SREČANJ
##########################################################################


@get('/srecanje/<srecanje:int>/premakni')
def premakni_srecanje(srecanje):
    return template(
        'urnik',
        premaknjeno_srecanje=srecanje,
        odlozena_srecanja=modeli.odlozena_srecanja(),
        srecanja=modeli.povezana_srecanja(srecanje),
        prosti_termini=modeli.prosti_termini(srecanje),
        next=request.headers.get('referer') or '/',
        prekrivanja={},
    )


@post('/srecanje/<srecanje:int>/premakni')
def premakni_srecanje(srecanje):
    dan = int(request.forms.dan)
    ura = int(request.forms.ura)
    ucilnica = int(request.forms.ucilnica)
    modeli.premakni_srecanje(srecanje, dan, ura, ucilnica)
    redirect(request.forms.next)


@post('/srecanje/<srecanje:int>/izbrisi')
def izbrisi(srecanje):
    modeli.izbrisi_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/')


@post('/srecanje/<srecanje:int>/podvoji')
def podvoji(srecanje):
    modeli.podvoji_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/')

@post('/srecanje/<srecanje:int>/odlozi')
def odlozi(srecanje):
    modeli.odlozi_srecanje(srecanje)
    redirect(request.headers.get('referer') or '/')


@post('/srecanje/<srecanje:int>/trajanje')
def trajanje_srecanja(srecanje):
    trajanje = int(request.forms.trajanje)
    modeli.nastavi_trajanje(srecanje, trajanje)
    redirect(request.headers.get('referer') or '/')


@get('/srecanje/<srecanje:int>/uredi')
def uredi_srecanje(srecanje):
    return template(
        'uredi_srecanje',
        srecanje=modeli.podatki_srecanja(srecanje),
        ucitelji=modeli.podatki_oseb(),
        predmeti=modeli.podatki_predmetov(),
        ucilnice=modeli.podatki_ucilnic(),
        next=request.headers.get('referer') or '/',
    )


@post('/srecanje/<srecanje:int>/uredi')
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


@route('/urnik')
def urnik():
    return template(
        'urnik',
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

@route('/fiziki')
def fiziki():
    return template(
        'urnik',
        srecanja=modeli.fiziki(),
        odlozena_srecanja=[],
        prekrivanja={},
    )

##########################################################################
# ZAGON APLIKACIJE
##########################################################################

if __name__ == '__main__':
    run(debug=True, reloader=True)
else:
    bottle.debug(True)
    app = default_app()
