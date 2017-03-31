import csv
import pypxlib
import os
import sqlite3

##########################################################################
# OSNOVNE NASTAVITVE
##########################################################################

IME_DATOTEKE = 'urnik.sqlite3'

SEMINARJI = (
    'OSN SEM',
    'GEOTOP SEM',
    'SAFA SEM',
    'SEJA',
    'GEO SEM',
    'ALG SEM',
    'KA SEM',
    'DM SEM',
    'FM SEM',
    'GRAALG SEM',
    'NA SEM',
    'SRE SEM',
    'TOP SEM',
    'MAT KOL',
)

POSEBNI_PREDMETI = {
    'GU': ('Govorilne ure', 'GU', None),
    'REZ': ('Rezervacija', 'REZ', None),
    'OSN SEM': ('Seminar za osnove', 'SEM-OSN', None),
    'GEOTOP SEM': ('Seminar za geometrijsko topologijo', 'SEM-GEOTOP', None),
    'SAFA SEM': ('Seminar za SAFA', 'SEM-SAFA', None),
    'SEJA': ('Seja', 'SEJA', None),
    'GEO SEM': ('Seminar za geometrijo', 'SEM-GEO', None),
    'ALG SEM': ('Seminar za algebro', 'SEM-ALG', None),
    'KA SEM': ('Seminar za kompleksno analizo', 'SEM-KA', None),
    'DM SEM': ('Seminar za diskretno matematiko', 'SEM-DM', None),
    'FM SEM': ('Seminar za finančno matematiko', 'SEM-FM', None),
    'GRAALG SEM': ('Seminar za GRAALG', 'SEM-GRAALG', None),
    'NA SEM': ('Seminar za numerično analizo', 'SEM-NA', None),
    'SRE SEM': ('Sredin seminar', 'SEM-SRE', None),
    'TOP SEM': ('Topološki seminar', 'SEM-TOP', None),
    'MAT KOL': ('Matematični kolokvij', 'SEM-MK', None),
    'ZGODMAT': ('Seminar za matematično zgodovino', 'SEM-ZGOD', None),
}

VIDNE_UCILNICE = (
    'P.01', 'P.02', 'P.05',
    '2.01', '2.02', '2.03', '2.04', '2.05',
    '3.04', '3.05', '3.06', '3.07', '3.10', '3.11', '3.12',
)

RACUNALNISKE_UCILNICE = (
    '3.10', '3.11', '3.12'
)

FIKTIVNE_UCILNICE = (
    '1.00001', '1.0001', '1.001', '1.01',
    'Z', 'ZZ', 'ZZZ', 'ZZZZ'
)

LETNIKI = {
    '1F': ('1FiMa', 1), '1I': ('1ISRM', 1), '1N': ('1Mate', 1), '1P': ('2PeMa', 1), 'A': ('1PrMa', 1),
    '2F': ('1FiMa', 2), '2I': ('1ISRM', 2), '2N': ('1Mate', 2), '2P': ('2PeMa', 2), 'B': ('1PrMa', 2),
    '3F': ('1FiMa', 3), '3I': ('1ISRM', 3), '3N': ('1Mate', 3), '3P': ('2PeMa', 3), 'C': ('1PrMa', 3),
    '4P': ('2PeMa', 4), '5P': ('2PeMa', 5),
    '4F': ('2FiMa', None), '4I': ('2ISRM', None), 'R': ('2Mate', None),
    'D': ('3Mate', None), 'S': ('3MaSt', None),
    'W': ('Fiz', None),
}

IZPUSCENI_LETNIKI = (
    '3M', 'Y', '4T', '2Z', '1M', '4U', '2M', '4M', 'Z', 'X'
)

POPRAVEK_PREDMETOV = {
    'SEM DM (KONVALINKA)': 'DM SEM (KONVALINKA)',
    'SAFA (ŠEMRL)': 'SAFA SEM (ŠEMRL)',
    'MM  (PRA)': 'MM (PRA)',
    'FIZ1': 'FIZ 1',
    'STAT  (PRA)': 'STAT (PRA)',
    'NM2 (F)': 'NM 2 (F)',
    'MATMOD': 'MM',
    'MAT (KI)': 'MAT (KEMINŽ)',
    'REZERVACIJA': 'REZ',
    'KOMA (REZERVACIJA)': 'REZ',
    'IPRM (REZ)': 'REZ',
    'VERJ (REZ)': 'REZ',
}

##########################################################################
# POMOŽNE FUNKCIJE
##########################################################################


def nalozi_paradox(koncnica):
    OSNOVA = '/Users/matija/Documents/urnik/uvoz/urnik 1617letni.'
    return pypxlib.Table(OSNOVA + koncnica, encoding='cp852')


def izlusci_predmet(predmet):
    if predmet[:3] == 'GU ':
        return 'GU'
    for niz in (' V1', ' V2', ' V3', ' V'):
        predmet = predmet.replace(niz, '')
    if predmet.startswith('REZ ') or predmet.startswith('REZERVACIJA'):
        predmet = 'REZ'
    predmet = POPRAVEK_PREDMETOV.get(predmet, predmet)
    if ' SEM' in predmet and not any(predmet.startswith(seminar) for seminar in SEMINARJI):
        predmet = predmet.replace(' SEM', '')
    return predmet


def izlusci_seminar(predmet):
    for seminar in SEMINARJI:
        if predmet.startswith(seminar) and predmet != seminar:
            return seminar


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

letniki = {
    letnik: {
        'smer': smer,
        'leto': leto
    }
    for
    letnik, (smer, leto)
    in
    LETNIKI.items()
}

velikost_ucilnice = {
    ucilnica.Predavalnica: ucilnica.Velikost for ucilnica in nalozi_paradox('uci')
}
ucilnice = {
    ucilnica: {
        'oznaka': ucilnica,
        'velikost': velikost_ucilnice.get(ucilnica),
        'racunalniska': ucilnica in RACUNALNISKE_UCILNICE,
        'skrita': ucilnica not in VIDNE_UCILNICE,
    }
    for
    ucilnica
    in
    {izlusci_ucilnico(srecanje.Predavalnica) for srecanje in nalozi_paradox('urn')}
    if
    ucilnica not in FIKTIVNE_UCILNICE
}

prevod_osebe = {(ime, priimek): oseba for oseba, ime, priimek in csv.reader(open('uvoz/prevod oseb.csv'))}
podatki_osebe = {
    prevod_osebe[(ime, priimek)]: (ime, priimek, email)
    for
    ime, priimek, email
    in
    csv.reader(open('uvoz/podatki oseb.csv'))
    if
    (ime, priimek) in prevod_osebe
}
domaca_stran_osebe = {oseba.Ime: oseba.Povezava for oseba in nalozi_paradox('lin')}
osebe = {}
for oseba in {urnik.Profesor for urnik in nalozi_paradox('urn')}:
    ime, priimek, email = podatki_osebe.get(oseba, ('', oseba, None))
    domaca_stran = domaca_stran_osebe.get(oseba)
    osebe[oseba] = {
        'ime': ime,
        'priimek': priimek,
        'email': email if email else None,
        'domaca_stran': domaca_stran if domaca_stran else None,
    }

prevod_predmeta = {(program, smer, predmet): oznaka for oznaka, program, smer, predmet in csv.reader(open('uvoz/prevod predmetov.csv'))}
podatki_predmeta = {
    prevod_predmeta[(program, smer, predmet)]: (ime, kratica, stevilo_studentov)
    for
    program, smer, predmet, ime, kratica, stevilo_studentov
    in
    csv.reader(open('uvoz/podatki predmetov.csv'))
    if
    (program, smer, predmet) in prevod_predmeta
}
predmeti = {}
for predmet in {izlusci_predmet(urnik.Predmet) for urnik in nalozi_paradox('urn')} | set(SEMINARJI):
    if izlusci_seminar(predmet):
        continue
    elif predmet in POSEBNI_PREDMETI:
        ime, kratica, stevilo_studentov = POSEBNI_PREDMETI[predmet]
    else:
        ime, kratica, stevilo_studentov = podatki_predmeta.get(predmet, (predmet, predmet, None))
    predmeti[predmet] = {
        'ime': ime,
        'kratica': kratica,
        'stevilo_studentov': stevilo_studentov,
        'letniki': set(),
        'slusatelji': set()
    }

bloki = {}
for srecanje in nalozi_paradox('urn'):
    predmet = izlusci_predmet(srecanje.Predmet)
    seminar = izlusci_seminar(predmet)
    if seminar:
        predmeti[seminar]['slusatelji'].add(srecanje.Profesor)
    else:
        for letnik in srecanje.Letnik.split():
            if letnik not in IZPUSCENI_LETNIKI:
                predmeti[predmet]['letniki'].add(letnik)
        ucilnica = izlusci_ucilnico(srecanje.Predavalnica)
        if ucilnica in FIKTIVNE_UCILNICE:
            continue
        tip = izlusci_tip(srecanje.Predmet)
        ucitelj = srecanje.Profesor
        predmet = izlusci_predmet(srecanje.Predmet)
        oznaka = izlusci_oznako(srecanje.Predmet)
        ura = srecanje.Ura
        bloki.setdefault((ucilnica, tip, oznaka, ucitelj, predmet),
                         set()).add((srecanje.Dan, srecanje.Ura))


srecanja = [
    {
        'ucilnica': ucilnica,
        'tip': tip,
        'oznaka': oznaka,
        'ucitelj': ucitelj,
        'predmet': predmet,
        'dan': dan,
        'ura': ura,
        'trajanje': trajanje,
    }
    for
    (ucilnica, tip, oznaka, ucitelj, predmet), ure in bloki.items()
    for
    dan, ura, trajanje
    in
    zdruzi_ure(ure)
]


##########################################################################
# USTVARJANJE BAZE
##########################################################################

os.remove(IME_DATOTEKE)
con = sqlite3.connect(IME_DATOTEKE)
con.row_factory = sqlite3.Row
con.execute('PRAGMA foreign_keys = ON')

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
        velikost     INTEGER,
        racunalniska BOOLEAN DEFAULT (0) 
                             NOT NULL,
        skrita       BOOLEAN DEFAULT (0) 
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
    CREATE TABLE slusatelji (
        predmet INTEGER REFERENCES predmet (id),
        oseba   INTEGER REFERENCES oseba (id),
        PRIMARY KEY (
            predmet,
            oseba
        )
    )
''')

con.execute('''
    CREATE TABLE oseba (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        ime          TEXT    NOT NULL,
        priimek      TEXT    NOT NULL,
        email        TEXT    UNIQUE,
        domaca_stran TEXT
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
        stevilo_studentov INTEGER
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
        (oznaka, velikost, racunalniska, skrita)
        VALUES (?, ?, ?, ?)
    ''', (
        ucilnica['oznaka'],
        ucilnica['velikost'],
        ucilnica['racunalniska'],
        ucilnica['skrita'],
    ))
    ucilnica_pk[kljuc] = cur.lastrowid


letnik_pk = {}
for kljuc, letnik in letniki.items():
    cur = con.execute('''
        INSERT INTO
        letnik
        (smer, leto)
        VALUES (?, ?)
    ''', (
        letnik['smer'],
        letnik['leto'],
    ))
    letnik_pk[kljuc] = cur.lastrowid


oseba_pk = {}
for kljuc, oseba in osebe.items():
    cur = con.execute('''
        INSERT INTO
        oseba
        (ime, priimek, email, domaca_stran)
        VALUES (?, ?, ?, ?)
    ''', (
        oseba['ime'],
        oseba['priimek'],
        oseba['email'],
        oseba['domaca_stran'],
    ))
    oseba_pk[kljuc] = cur.lastrowid


predmet_pk = {}
for kljuc, predmet in predmeti.items():
    cur = con.execute('''
        INSERT INTO
        predmet
        (ime, kratica, stevilo_studentov)
        VALUES (?, ?, ?)
    ''', (
        predmet['ime'],
        predmet['kratica'],
        predmet['stevilo_studentov'],
    ))
    predmet_pk[kljuc] = cur.lastrowid
    for letnik in predmet['letniki']:
        con.execute('''
            INSERT INTO
            predmet_letnik
            (predmet, letnik)
            VALUES (?, ?)
        ''', (
            predmet_pk[kljuc],
            letnik_pk[letnik],
        ))
    for oseba in predmet['slusatelji']:
        con.execute('''
            INSERT INTO
            slusatelji
            (predmet, oseba)
            VALUES (?, ?)
        ''', (
            predmet_pk[kljuc],
            oseba_pk[oseba],
        ))

for srecanje in srecanja:
    cur = con.execute('''
        INSERT INTO
        srecanje
        (ucilnica, tip, oznaka, ucitelj, predmet, dan, ura, trajanje)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ucilnica_pk[srecanje['ucilnica']],
        srecanje['tip'],
        srecanje['oznaka'],
        oseba_pk[srecanje['ucitelj']],
        predmet_pk[srecanje['predmet']],
        srecanje['dan'],
        srecanje['ura'],
        srecanje['trajanje'],
    ))

con.commit()
