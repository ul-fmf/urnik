from bottle import route, run, template, static_file
import modeli


@route('/')
def domaca_stran():
    return template(
        'domaca_stran',
        letniki=modeli.seznam_letnikov(),
        osebe=modeli.seznam_oseb(),
        ucilnice=modeli.seznam_ucilnic(),
    )


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


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

run(debug=True, reloader=True)