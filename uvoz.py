import csv
import pypxlib
import sqlite3

##########################################################################
# OSNOVNE NASTAVITVE
##########################################################################

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
con.execute('PRAGMA foreign_keys = ON')

##########################################################################
# POMOŽNE FUNKCIJE
##########################################################################


def nalozi_paradox(koncnica):
    OSNOVA = '/Users/matija/Documents/urnik/uvoz/urnik 1617letni.'
    return pypxlib.Table(OSNOVA + koncnica, encoding='cp852')


def izlusci_predmet(predmet):
    if predmet[:3] == 'GU ':
        return 'GU'
    for niz in (' V1', ' V2', ' V3', ' V', ' SEM'):
        predmet = predmet.replace(niz, '')
    return predmet


def izlusci_tip(predmet):
    if any(tip in predmet for tip in (' V1', ' V2', ' V3', ' V')):
        return 'V'
    elif any(tip in predmet for tip in ('SEM', ' S1', ' S2')):
        return 'S'
    else:
        return 'P'


def izlusci_oznako(predmet):
    if any(tip in predmet for tip in (' V1', ' S1')):
        return 1
    elif any(tip in predmet for tip in (' V2', ' S2')):
        return 2
    elif ' V3' in predmet:
        return 3


def izlusci_ucilnico(ucilnica):
    if ucilnica[0] == '(' and ucilnica[-1] == ')':
        return ucilnica[1:-1]
    else:
        return ucilnica


def opozorilo(niz):
    print(niz)


def zdruzi_ure(ure):
    zdruzene_ure = {}
    dan_zacetka, ura_zacetka, trajanje = None, None, 1
    for dan, ura in sorted(ure):
        if dan_zacetka is None:
            dan_zacetka, ura_zacetka = dan, ura
        elif (dan_zacetka, ura_zacetka + trajanje) == (dan, ura):
            trajanje += 1
        else:
            yield dan_zacetka, ura_zacetka, trajanje
            dan_zacetka, ura_zacetka, trajanje = dan, ura, 1
    yield dan_zacetka, ura_zacetka, trajanje

##########################################################################
# BRANJE STARIH PODATKOV
##########################################################################

ucilnice = {}
for ucilnica in nalozi_paradox('uci'):
    if ucilnica.Predavalnica == '4.27':
        continue
    ucilnice[ucilnica.Predavalnica] = {
        'oznaka': ucilnica.Predavalnica,
        'velikost': ucilnica.Velikost,
        'racunalniska': ucilnica.Predavalnica[:3] == '3.1',
    }
NEZNANE_UCILNICE = {izlusci_ucilnico(
    urnik.Predavalnica) for urnik in nalozi_paradox('urn')}
for neznana in NEZNANE_UCILNICE:
    if neznana not in ucilnice:
        ucilnice[neznana] = {
            'oznaka': neznana,
            'velikost': 1,
            'racunalniska': False,
        }

SMERI = {
    '1F': ('1FiMa', 1), '1I': ('1ISRM', 1), '1N': ('1Mate', 1), '1P': ('2PeMa', 1), 'A': ('1PrMa', 1),
    '2F': ('1FiMa', 2), '2I': ('1ISRM', 2), '2N': ('1Mate', 2), '2P': ('2PeMa', 2), 'B': ('1PrMa', 2),
    '3F': ('1FiMa', 3), '3I': ('1ISRM', 3), '3N': ('1Mate', 3), '3P': ('2PeMa', 3), 'C': ('1PrMa', 3),
    '4P': ('2PeMa', 4), '5P': ('2PeMa', 5),
    '4F': ('2FiMa', None), '4I': ('2ISRM', None), 'R': ('2Mate', None),
    'D': ('3Mate', None), 'S': ('3MaSt', None),
    'W': ('Fiz', None), 'X': ('Ostalo', None), 'Z': ('Rez', None),
}
letniki = {}
for oznaka, (smer, leto) in SMERI.items():
    letniki[oznaka] = {
        'smer': smer,
        'leto': leto,
    }

podatki_osebe = {}
with open('uvoz/podatki oseb.csv') as csvfile:
    for ime, priimek, email in csv.reader(csvfile):
        podatki_osebe[(ime, priimek)] = (ime, priimek, email)
prevod_osebe = {}
with open('uvoz/prevod oseb.csv') as csvfile:
    for oznaka, ime, priimek in csv.reader(csvfile):
        prevod_osebe[oznaka] = (ime, priimek)

OSEBE = {izlusci_predmet(urnik.Profesor) for urnik in nalozi_paradox('urn')}
osebe = {}
for oseba in OSEBE:
    ime, priimek, email = podatki_osebe.get(
        prevod_osebe.get(oseba),
        ('???', oseba, None)
    )
    osebe[oseba] = {
        'ime': ime,
        'priimek': priimek,
        'email': email if email else None,
    }

podatki_predmeta = {}
with open('uvoz/podatki predmetov.csv') as csvfile:
    for program, smer, predmet, ime, kratica, stevilo_studentov in csv.reader(csvfile):
        podatki_predmeta[(program, smer, predmet)] = (ime, kratica, stevilo_studentov)
prevod_predmeta = {}
with open('uvoz/prevod predmetov.csv') as csvfile:
    for oznaka, program, smer, predmet in csv.reader(csvfile):
        prevod_predmeta[oznaka] = (program, smer, predmet)

PREDMETI = {izlusci_predmet(urnik.Predmet) for urnik in nalozi_paradox('urn')}
predmeti = {}
for predmet in PREDMETI:
    if predmet == 'GU':
        ime, kratica, stevilo_studentov = 'Govorilne ure', 'GU', None
    else:
        ime, kratica, stevilo_studentov = podatki_predmeta.get(
            prevod_predmeta.get(predmet),
            (predmet, predmet, None)
        )
    predmeti[predmet] = {
        'ime': ime,
        'kratica': kratica,
        'stevilo_studentov': stevilo_studentov,
        'racunalniski': False,
    }
for urnik in nalozi_paradox('urn'):
    predmet = izlusci_predmet(urnik.Predmet)
    smeri = sorted(urnik.Letnik.split())
    if 'smeri' not in predmeti[predmet]:
        predmeti[predmet]['smeri'] = smeri
    elif predmeti[predmet]['smeri'] != smeri:
        opozorilo('Predmet {} ima včasih vpisane smeri {}, včasih pa {}'.format(
            predmet,
            ', '.join(smeri),
            ', '.join(predmeti[predmet]['smeri'])
        ))
bloki = {}
for urnik in nalozi_paradox('urn'):
    ucilnica = urnik.Predavalnica
    tip = izlusci_tip(urnik.Predmet)
    ucitelj = urnik.Profesor
    predmet = izlusci_predmet(urnik.Predmet)
    oznaka = izlusci_oznako(urnik.Predmet)
    ura = urnik.Ura
    bloki.setdefault((ucilnica, tip, oznaka, ucitelj, predmet),
                     set()).add((urnik.Dan, urnik.Ura))
srecanja = []
for (ucilnica, tip, oznaka, ucitelj, predmet), ure in bloki.items():
    for dan, ura, trajanje in zdruzi_ure(ure):
        srecanja.append({
            'ucilnica': ucilnica,
            'tip': tip,
            'oznaka': oznaka,
            'ucitelj': ucitelj,
            'predmet': predmet,
            'dan': dan,
            'ura': ura,
            'trajanje': trajanje,
        })


##########################################################################
# USTVARJANJE BAZE
##########################################################################

con.execute('''
    CREATE TABLE srecanje (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        ucilnica INTEGER REFERENCES ucilnica (id),
        ura      INTEGER CHECK (ura BETWEEN 7 AND 19),
        dan      INTEGER CHECK (dan BETWEEN 1 AND 5),
        trajanje INTEGER CONSTRAINT [srečanje se ne konča do 20h] CHECK (ura + trajanje <= 20),
        tip      CHAR    CHECK (tip IN ('P', 'S', 'V', 'L') ) 
                         NOT NULL,
        ucitelj  INTEGER REFERENCES oseba (id),
        predmet  INTEGER REFERENCES predmet (id),
        oznaka   CHAR
    )
''')
con.execute('''
    CREATE TABLE ucilnica (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        oznaka       TEXT    UNIQUE
                             NOT NULL,
        velikost     INTEGER NOT NULL
                             CHECK (velikost > 0),
        racunalniska BOOLEAN DEFAULT (0) 
                             NOT NULL
    )
''')
con.execute('''
    CREATE TABLE predmet_letnik (
        predmet INTEGER REFERENCES predmet (id),
        letnik  INTEGER REFERENCES letnik (id),
        PRIMARY KEY (
            predmet,
            letnik
        )
    )
''')
con.execute('''
    CREATE TABLE oseba (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        ime     TEXT    NOT NULL,
        priimek TEXT    NOT NULL,
        email   TEXT    UNIQUE
    )
''')
con.execute('''
    CREATE TABLE letnik (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        smer TEXT,
        leto INTEGER CHECK (leto BETWEEN 1 AND 5) 
    )
''')
con.execute('''
    CREATE TABLE predmet (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        ime               TEXT    NOT NULL,
        kratica           TEXT,
        stevilo_studentov INTEGER,
        racunalniski      BOOLEAN DEFAULT (0) 
    )
''')

##########################################################################
# PISANJE V BAZO
##########################################################################

ucilnica_pk = {}
for kljuc, ucilnica in ucilnice.items():
    cur = con.execute('''
        INSERT INTO
        ucilnica
        (oznaka, velikost, racunalniska)
        VALUES (?, ?, ?)
    ''', (ucilnica['oznaka'], ucilnica['velikost'], ucilnica['racunalniska']))
    ucilnica_pk[kljuc] = cur.lastrowid


letnik_pk = {}
for kljuc, letnik in letniki.items():
    cur = con.execute('''
        INSERT INTO
        letnik
        (smer, leto)
        VALUES (?, ?)
    ''', (letnik['smer'], letnik['leto']))
    letnik_pk[kljuc] = cur.lastrowid

oseba_pk = {}
for kljuc, oseba in osebe.items():
    cur = con.execute('''
        INSERT INTO
        oseba
        (ime, priimek, email)
        VALUES (?, ?, ?)
    ''', (oseba['ime'], oseba['priimek'], oseba['email']))
    oseba_pk[kljuc] = cur.lastrowid

predmet_pk = {}
for kljuc, predmet in predmeti.items():
    cur = con.execute('''
        INSERT INTO
        predmet
        (ime, kratica, stevilo_studentov, racunalniski)
        VALUES (?, ?, ?, ?)
    ''', (predmet['ime'], predmet['kratica'], predmet['stevilo_studentov'], predmet['racunalniski']))
    predmet_pk[kljuc] = cur.lastrowid
    for smer in predmet['smeri']:
        if smer in letnik_pk:
            con.execute('''
                INSERT INTO
                predmet_letnik
                (predmet, letnik)
                VALUES (?, ?)
            ''', (predmet_pk[kljuc], letnik_pk[smer]))
        else:
            opozorilo('Predmet {} ima vpisano smer {}, ki ne obstaja'.format(
                kljuc,
                smer
            ))

for srecanje in srecanja:
    ucilnica = izlusci_ucilnico(srecanje['ucilnica'])
    cur = con.execute('''
        INSERT INTO
        srecanje
        (ucilnica, tip, oznaka, ucitelj, predmet, dan, ura, trajanje)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ucilnica_pk[ucilnica],
        srecanje['tip'],
        srecanje['oznaka'],
        oseba_pk[srecanje['ucitelj']],
        predmet_pk[srecanje['predmet']],
        srecanje['dan'],
        srecanje['ura'],
        srecanje['trajanje']
    ))

con.commit()
