from bottle import route, run, template, get, post, request, redirect
import modeli


################################################################################
# DOMAČA STRAN
################################################################################

@route('/')
def domaca_stran():
    return template(
        'domaca_stran',
        letniki=modeli.seznam_letnikov(),
        osebe=modeli.seznam_oseb(),
        ucilnice=modeli.seznam_ucilnic(),
    )

################################################################################
# UREJANJE
################################################################################


@get('/letnik/<letnik:int>/uredi')
def uredi_letnik(letnik):
    return template(
        'uredi_letnik',
        letnik=modeli.letnik(letnik)
    )


@post('/letnik/<letnik:int>/uredi')
def uredi_letnik_post(letnik):
    smer = request.forms.smer
    leto = int(request.forms.leto)
    stevilo_studentov = int(request.forms.stevilo_studentov)
    modeli.uredi_letnik(letnik, smer, leto, stevilo_studentov)
    redirect('/')


@get('/oseba/<oseba:int>/uredi')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.oseba(oseba)
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
        ucilnica=modeli.ucilnica(ucilnica)
    )


@post('/ucilnica/<ucilnica:int>/uredi')
def uredi_ucilnico_post(ucilnica):
    oznaka = request.forms.oznaka
    velikost = int(request.forms.velikost)
    racunalniska = request.forms.racunalniska
    modeli.uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska)
    redirect('/')


################################################################################
# UREJANJE SREČANJ
################################################################################


@get('/srecanje/<srecanje:int>/premakni')
def premakni_srecanje(srecanje):
    return template(
        'urnik',
        premaknjeno_srecanje=srecanje,
        srecanja=modeli.povezana_srecanja(srecanje),
        prosti_termini=modeli.prosti_termini(srecanje),
        next=request.headers.get('referer') or '/',
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


@post('/srecanje/<srecanje:int>/trajanje')
def trajanje_srecanja(srecanje):
    trajanje = int(request.forms.trajanje)
    modeli.nastavi_trajanje(srecanje, trajanje)
    redirect(request.headers.get('referer') or '/')


@get('/srecanje/<srecanje:int>/uredi')
def uredi_srecanje(srecanje):
    return template(
        'uredi_srecanje',
        srecanje=modeli.srecanje(srecanje),
        ucitelji=modeli.seznam_oseb(),
        letniki=modeli.seznam_letnikov(),
    )


@post('/srecanje/<srecanje:int>/uredi')
def uredi_srecanje_post(srecanje):
    ucitelj = int(request.forms.ucitelj)
    ucilnica = int(request.forms.ucilnica)
    tip = request.forms.tip
    modeli.uredi_srecanje(srecanje, ucitelj, ucilnica, tip)
    redirect('/')

################################################################################
# PRIKAZ URNIKA
################################################################################


@route('/urnik')
def urnik():
    return template(
        'urnik',
        srecanja=modeli.urnik(
            letniki=[int(letnik) for letnik in request.query.getall('letnik')],
            osebe=[int(oseba) for oseba in request.query.getall('oseba')],
            ucilnice=[int(ucilnica) for ucilnica in request.query.getall('ucilnica')],
        )
    )


################################################################################
# ZAGON APLIKACIJE
################################################################################

run(debug=True, reloader=True)
