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
    smer = request.forms.smer
    leto = int(request.forms.leto)
    modeli.uredi_letnik(letnik, smer, leto)
    redirect('/')


@get('/oseba/<oseba:int>/uredi')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.podatki_osebe(oseba)
    )


@post('/oseba/<oseba:int>/uredi')
def uredi_osebo_post(oseba):
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    modeli.uredi_osebo(oseba, ime, priimek, email)
    redirect('/')


@get('/ucilnica/<ucilnica:int>/uredi')
def uredi_ucilnico(ucilnica):
    return template(
        'uredi_ucilnico',
        ucilnica=modeli.podatki_ucilnice(ucilnica)
    )


@post('/ucilnica/<ucilnica:int>/uredi')
def uredi_ucilnico_post(ucilnica):
    oznaka = request.forms.oznaka
    velikost = None if request.forms.velikost is None else int(request.forms.velikost)
    racunalniska = request.forms.racunalniska
    modeli.uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska)
    redirect('/')


@get('/predmet/<predmet:int>/uredi')
def uredi_predmet(predmet):
    return template(
        'uredi_predmet',
        predmet=modeli.podatki_predmeta(predmet),
        letniki=modeli.podatki_letnikov()
    )


@post('/predmet/<predmet:int>/uredi')
def uredi_predmet_post(predmet):
    ime = request.forms.ime
    kratica = request.forms.kratica
    stevilo_studentov = None if request.forms.stevilo_studentov is '' else int(request.forms.stevilo_studentov)
    letniki = [int(letnik) for letnik in request.forms.getall('letniki')]
    modeli.uredi_predmet(predmet, ime, kratica, stevilo_studentov, letniki)
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
    smer = request.forms.smer
    leto = int(request.forms.leto)
    modeli.ustvari_letnik(smer, leto)
    redirect('/')


@get('/oseba/ustvari')
def ustvari_osebo():
    return template(
        'uredi_osebo'
    )


@post('/oseba/ustvari')
def ustvari_osebo_post():
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    modeli.ustvari_osebo(ime, priimek, email)
    redirect('/')


@get('/ucilnica/ustvari')
def ustvari_ucilnico():
    return template(
        'uredi_ucilnico'
    )


@post('/ucilnica/ustvari')
def ustvari_ucilnico_post():
    oznaka = request.forms.oznaka
    velikost = int(request.forms.velikost)
    racunalniska = request.forms.racunalniska
    skrita = request.forms.skrita
    modeli.uredi_ucilnico(oznaka, velikost, racunalniska, skrita)
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
        prekrivanje_ucilnic=modeli.prekrivanje_ucilnic(),
        prekrivanje_oseb=modeli.prekrivanje_oseb(),
        prekrivanje_letnikov=modeli.prekrivanje_letnikov(),
        podatki_srecanj=modeli.podatki_srecanj(),
        podatki_oseb=modeli.podatki_oseb(),
        podatki_ucilnic=modeli.podatki_ucilnic(),
        podatki_predmetov=modeli.podatki_predmetov(),
        podatki_letnikov=modeli.podatki_letnikov(),
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
        srecanje=modeli.nalozi_srecanje(srecanje),
        ucitelji=modeli.podatki_oseb(),
        predmeti=modeli.seznam_predmetov(),
        next=request.headers.get('referer') or '/',
    )


@post('/srecanje/<srecanje:int>/uredi')
def uredi_srecanje_post(srecanje):
    ucitelj = int(request.forms.ucitelj)
    predmet = int(request.forms.predmet)
    tip = request.forms.tip
    oznaka = request.forms.oznaka
    modeli.uredi_srecanje(srecanje, ucitelj, predmet, tip, oznaka)
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
        prekrivanje_ucilnic=modeli.prekrivanje_ucilnic(),
        prekrivanje_oseb=modeli.prekrivanje_oseb(),
        prekrivanje_letnikov=modeli.prekrivanje_letnikov(),
        podatki_srecanj=modeli.podatki_srecanj(),
        podatki_oseb=modeli.podatki_oseb(),
        podatki_ucilnic=modeli.podatki_ucilnic(),
        podatki_predmetov=modeli.podatki_predmetov(),
        podatki_letnikov=modeli.podatki_letnikov(),
    )

@route('/fiziki')
def fiziki():
    return template(
        'urnik',
        srecanja=modeli.fiziki(),
        prekrivanje_ucilnic=[],
        prekrivanje_oseb=[],
        prekrivanje_letnikov=[],
        odlozena_srecanja=[],
    )

##########################################################################
# ZAGON APLIKACIJE
##########################################################################

if __name__ == '__main__':
    run(debug=True, reloader=True)
else:
    bottle.debug(True)
    app = default_app()
