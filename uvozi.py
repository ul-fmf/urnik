import django
import sqlite3
from django.core import management
django.setup()
from urnik.models import Oseba, Letnik, Ucilnica, Predmet, Srecanje
from django.contrib.auth.models import User

def blankify(x):
    return x if x else ''

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
management.call_command('flush', verbosity=1, interactive=False)
management.call_command('migrate', verbosity=1, interactive=False)

oseba_dict = {}
for row in con.execute('SELECT * FROM oseba'):
    oseba_old = dict(row)
    oseba_new = Oseba(
        ime=oseba_old.pop('ime'),
        priimek=oseba_old.pop('priimek'),
        email=blankify(oseba_old.pop('email')),
        domaca_stran=blankify(oseba_old.pop('domaca_stran')),
    )
    oseba_new.save()
    oseba_dict[oseba_old.pop('id')] = oseba_new
    assert oseba_old == {}

letnik_dict = {}
for row in con.execute('SELECT * FROM letnik'):
    letnik_old = dict(row)
    letnik_new = Letnik(
        smer=letnik_old.pop('smer'),
        leto=letnik_old.pop('leto'),
    )
    letnik_new.save()
    letnik_dict[letnik_old.pop('id')] = letnik_new
    assert letnik_old == {}

ucilnica_dict = {}
for row in con.execute('SELECT * FROM ucilnica'):
    ucilnica_old = dict(row)
    ucilnica_new = Ucilnica(
        oznaka=ucilnica_old.pop('oznaka'),
        velikost=ucilnica_old.pop('velikost'),
        racunalniska=ucilnica_old.pop('racunalniska'),
        vidna=not ucilnica_old.pop('skrita'),
    )
    ucilnica_new.save()
    ucilnica_dict[ucilnica_old.pop('id')] = ucilnica_new
    assert ucilnica_old == {}

predmet_dict = {}
for row in con.execute('SELECT * FROM predmet'):
    predmet_old = dict(row)
    predmet_new = Predmet(
        ime=predmet_old.pop('ime'),
        kratica=predmet_old.pop('kratica'),
        stevilo_studentov=predmet_old.pop('stevilo_studentov'),
    )
    predmet_new.save()
    predmet_dict[predmet_old.pop('id')] = predmet_new
    assert predmet_old == {}

srecanje_dict = {}
for row in con.execute('SELECT * FROM srecanje'):
    srecanje_old = dict(row)
    srecanje_new = Srecanje(
        ucilnica=ucilnica_dict[srecanje_old.pop('ucilnica')],
        ura=srecanje_old.pop('ura'),
        dan=srecanje_old.pop('dan'),
        trajanje=srecanje_old.pop('trajanje'),
        tip=srecanje_old.pop('tip'),
        ucitelj=oseba_dict[srecanje_old.pop('ucitelj')],
        predmet=predmet_dict[srecanje_old.pop('predmet')],
        oznaka=blankify(srecanje_old.pop('oznaka')),
    )
    srecanje_new.save()
    srecanje_dict[srecanje_old.pop('id')] = srecanje_new
    assert srecanje_old == {}

for row in con.execute('SELECT * FROM slusatelji'):
    predmet_dict[row['predmet']].slusatelji.add(oseba_dict[row['oseba']])
    predmet_dict[row['predmet']].save()

for row in con.execute('SELECT * FROM predmet_letnik'):
    predmet_dict[row['predmet']].letniki.add(letnik_dict[row['letnik']])
    predmet_dict[row['predmet']].save()

User.objects.create_superuser(username='admin', password='admin',
                              email='matija+admin@pretnar.info',
                              first_name='Adminko', last_name='Admin')
