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


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

run(debug=True, reloader=True)