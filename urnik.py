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
# URNIKI LETNIKOV, OSEB IN UČILNIC
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
# UREJANJE LETNIKOV, OSEB IN UČILNIC
################################################################################

@get('/letnik/<letnik>/uredi')
def uredi_letnik(letnik):
    return template(
        'uredi_letnik',
        letnik=modeli.letnik(letnik)
    )


@post('/letnik/<letnik>/uredi')
def uredi_letnik_post(letnik):
    letnik = request.forms.letnik
    leto = int(request.forms.leto)
    smer = request.forms.smer
    stevilo_studentov = int(request.forms.stevilo_studentov)
    modeli.uredi_letnik(letnik, leto, smer, stevilo_studentov)
    redirect('/')


@get('/oseba/<oseba>/uredi')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.oseba(oseba)
    )


@post('/oseba/<oseba>/uredi')
def uredi_osebo_post(oseba):
    oseba = request.forms.oseba
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    modeli.uredi_osebo(oseba, ime, priimek, email)
    redirect('/')


@get('/ucilnica/<ucilnica>/uredi')
def uredi_ucilnico(ucilnica):
    return template(
        'uredi_ucilnico',
        ucilnica=modeli.ucilnica(ucilnica)
    )


@post('/ucilnica/<ucilnica>/uredi')
def uredi_ucilnico_post(ucilnica):
    ucilnica = request.forms.ucilnica
    oznaka = request.forms.oznaka
    velikost = request.forms.velikost
    racunalniska = request.forms.racunalniska
    modeli.uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska)
    redirect('/')

################################################################################
# ZAGON APLIKACIJE
################################################################################

run(debug=True, reloader=True)
