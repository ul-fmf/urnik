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

@route('/letnik/<letnik>/urnik')
def urnik_letnika(letnik):
    return template(
        'urnik',
        srecanja=modeli.urnik_letnika(letnik)
    )


@route('/oseba/<oseba>/urnik')
def urnik_osebe(oseba):
    return template(
        'urnik',
        srecanja=modeli.urnik_osebe(oseba)
    )


@route('/ucilnica/<ucilnica>/urnik')
def urnik_ucilnice(ucilnica):
    return template(
        'urnik',
        srecanja=modeli.urnik_ucilnice(ucilnica)
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
def uredi_letnik(letnik):
    letnik = request.forms.get('letnik')
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    email = request.forms.get('email')
    modeli.uredi_letnik(letnik, ime, priimek, email)
    redirect('/')

@get('/oseba/<oseba>/uredi')
def uredi_osebo(oseba):
    return template(
        'uredi_osebo',
        oseba=modeli.oseba(oseba)
    )

@post('/oseba/<oseba>/uredi')
def uredi_osebo_submit(oseba):
    oseba = request.forms.get('oseba')
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    email = request.forms.get('email')
    modeli.uredi_osebo(oseba, ime, priimek, email)
    redirect('/')

@get('/ucilnica/<ucilnica>/uredi')
def uredi_ucilnico(ucilnica):
    return template(
        'uredi_ucilnico',
        ucilnica=modeli.ucilnica(ucilnica)
    )

@post('/ucilnica/<ucilnica>/uredi')
def uredi_ucilnico(ucilnica):
    ucilnica = request.forms.get('ucilnica')
    oznaka = request.forms.get('oznaka')
    velikost = request.forms.get('velikost')
    racunalniska = request.forms.get('racunalniska', 0)
    print(racunalniska)
    modeli.uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska)
    redirect('/')




run(debug=True, reloader=True)