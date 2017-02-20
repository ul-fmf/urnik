from bottle import route, run, template, get, post, request, redirect, default_app
import bottle
import modeli


##########################################################################
# DOMAČA STRAN
##########################################################################

@route('/index.html')
def index_html():
    redirect('http://www.fmf.uni-lj.si/studij-matematike/urnik/')

@route('/<url>/index.html')
def index_html(url):
    redirect('http://www.fmf.uni-lj.si/studij-matematike/urnik/')

@route('/<url1>/<url2>/index.html')
def index_html(url1, url2):
    redirect('http://www.fmf.uni-lj.si/studij-matematike/urnik/')

@route('/')
def zacetna_stran():
    smeri = {}
    for letnik in modeli.podatki_letnikov().values():
        if letnik['leto']:
            letnik['opis'] = '{}, {}. letnik'.format(letnik['smer'], letnik['leto'])
        else:
            letnik['opis'] = letnik['smer']
        try:
            smer, opis = letnik['opis'].split(',')
            smeri.setdefault(smer, []).append((letnik['id'], opis))
        except:
            pass
    return template(
        'zacetna_stran',
        smeri=smeri,
        letniki=modeli.podatki_letnikov(),
        osebe=modeli.podatki_oseb(kljuci=modeli.kljuci_relevantnih_oseb()),
        ucilnice=modeli.podatki_ucilnic(),
    )

@route('/uredi/')
def uredi_zacetna_stran():
    return template(
        'uredi_zacetna_stran',
        letniki=modeli.podatki_letnikov(),
        osebe=modeli.podatki_oseb(),
        ucilnice=modeli.podatki_ucilnic(),
        predmeti=modeli.podatki_predmetov(),
    )

##########################################################################
# UREJANJE
##########################################################################


@get('/uredi/letnik/<letnik:int>/')
def uredi_letnik(letnik):
    return template(
        'uredi_letnik',
        letnik=modeli.podatki_letnika(letnik)
    )


@post('/uredi/letnik/<letnik:int>/')
def uredi_letnik_post(letnik):
    modeli.shrani_letnik({
        'id': letnik,
        'smer': request.forms.smer,
        'leto': int(request.forms.leto) if request.forms.leto else None,
    })
    redirect('/uredi/')


@get('/uredi/oseba/<oseba:int>/')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.podatki_osebe(oseba)
    )


@post('/uredi/oseba/<oseba:int>/')
def uredi_osebo_post(oseba):
    modeli.shrani_osebo({
        'id': oseba,
        'ime': request.forms.ime,
        'priimek': request.forms.priimek,
        'email': request.forms.email if request.forms.email else None,
    })
    redirect('/uredi/')


@get('/uredi/ucilnica/<ucilnica:int>/')
def uredi_ucilnico(ucilnica):
    return template(
        'uredi_ucilnico',
        ucilnica=modeli.podatki_ucilnice(ucilnica)
    )


@post('/uredi/ucilnica/<ucilnica:int>/')
def uredi_ucilnico_post(ucilnica):
    modeli.shrani_ucilnico({
        'id': ucilnica,
        'oznaka': request.forms.oznaka,
        'velikost': int(request.forms.velikost) if request.forms.velikost else None,
        'racunalniska': bool(request.forms.racunalniska),
        'skrita': bool(request.forms.skrita),
    })
    redirect('/uredi/')


@get('/uredi/predmet/<predmet:int>/')
def uredi_predmet(predmet):
    return template(
        'uredi_predmet',
        predmet=modeli.podatki_predmeta(predmet),
        letniki=modeli.podatki_letnikov(),
        slusatelji=modeli.podatki_oseb(),
    )


@post('/uredi/predmet/<predmet:int>/')
def uredi_predmet_post(predmet):
    ime = request.forms.ime
    kratica = request.forms.kratica
    stevilo_studentov = None if request.forms.stevilo_studentov is '' else int(request.forms.stevilo_studentov)
    letniki = [int(letnik) for letnik in request.forms.getall('letniki')]
    slusatelji = [int(slusatelj) for slusatelj in request.forms.getall('slusatelji')]
    modeli.uredi_predmet(predmet, ime, kratica, stevilo_studentov, letniki, slusatelji)
    redirect('/uredi/')

##########################################################################
# USTVARJANJE
##########################################################################


@get('/uredi/letnik/ustvari/')
def ustvari_letnik():
    return template(
        'uredi_letnik'
    )


@post('/uredi/letnik/ustvari/')
def ustvari_letnik_post():
    modeli.shrani_letnik({
        'smer': request.forms.smer,
        'leto': int(request.forms.leto),
    })
    redirect('/uredi/')


@get('/uredi/oseba/ustvari/')
def ustvari_osebo():
    return template(
        'uredi_osebo'
    )


@post('/uredi/oseba/ustvari/')
def ustvari_osebo_post():
    modeli.shrani_osebo({
        'ime': request.forms.ime,
        'priimek': request.forms.priimek,
        'email': request.forms.email if request.forms.email else None,
    })
    redirect('/uredi/')


@get('/uredi/ucilnica/ustvari/')
def ustvari_ucilnico():
    return template(
        'uredi_ucilnico'
    )


@post('/uredi/ucilnica/ustvari/')
def ustvari_ucilnico_post():
    modeli.shrani_ucilnico({
        'oznaka': request.forms.oznaka,
        'velikost': int(request.forms.velikost) if request.forms.velikost else None,
        'racunalniska': bool(request.forms.racunalniska),
        'skrita': bool(request.forms.skrita),
    })
    redirect('/uredi/')


@get('/uredi/predmet/ustvari/')
def ustvari_predmet():
    return template(
        'uredi_predmet',
        letniki=modeli.podatki_letnikov(),
        slusatelji=modeli.podatki_oseb(),
    )


@post('/uredi/predmet/ustvari/')
def ustvari_predmet_post():
    ime = request.forms.ime
    kratica = request.forms.kratica
    stevilo_studentov = None if request.forms.stevilo_studentov is '' else int(request.forms.stevilo_studentov)
    letniki = [int(letnik) for letnik in request.forms.getall('letniki')]
    slusatelji = [int(letnik) for letnik in request.forms.getall('slusatelji')]
    modeli.ustvari_predmet(ime, kratica, stevilo_studentov, letniki, slusatelji)
    redirect('/uredi/')


##########################################################################
# UREJANJE SREČANJ
##########################################################################


@get('/uredi/srecanje/<srecanje:int>/premakni/')
def premakni_srecanje(srecanje):
    return template(
        'uredi_urnik',
        premaknjeno_srecanje=srecanje,
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
    modeli.izbrisi_srecanje(srecanje)
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
        'uredi_urnik',
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
