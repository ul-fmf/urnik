import sqlite3
from pypxlib import Table

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
con.execute('PRAGMA foreign_keys = ON')

con.execute('DELETE FROM predmet_letnik')
con.execute('DELETE FROM srecanje')
con.execute('DELETE FROM letnik')
con.execute('DELETE FROM oseba')
con.execute('DELETE FROM predmet')
con.execute('DELETE FROM ucilnica')
con.execute('UPDATE sqlite_sequence SET seq = 0')

OSNOVA = '/Users/matija/Documents/urnik/uvoz/urnik 1617letni.'
LINKI = OSNOVA + 'lin'  #Row(Ime='Velušček', Povezava='http://www.fmf.uni-lj.si/si/imenik/3529/')
URNIK = OSNOVA + 'urn'  # Row(Dan=5, Ura=10, Predavalnica='2.05', Predmet='UVP', Profesor='Pretnar', Letnik='1N 1P', VIS=True)

SMERI = {
    '1F': ('1FiMa', 1), '1I': ('1ISRM', 1), '1N': ('1Mate', 1), '1P': ('2PeMa', 1), 'A': ('1PrMa', 1),
    '2F': ('1FiMa', 2), '2I': ('1ISRM', 2), '2N': ('1Mate', 2), '2P': ('2PeMa', 2), 'B': ('1PrMa', 2),
    '3F': ('1FiMa', 3), '3I': ('1ISRM', 3), '3N': ('1Mate', 3), '3P': ('2PeMa', 3), 'C': ('1PrMa', 3),
    '4P': ('2PeMa', 4), '5P': ('2PeMa', 5),
    '4F': ('2FiMa', None), '4I': ('2ISRM', None), 'R': ('2Mate', None),
    'D': ('3Mate', None), 'S': ('3MaSt', None),
    'W': ('Fiz', None), 'X': ('Ostalo', None), 'Z': ('Rez', None),
}

def izlusci_predmet(predmet):
    for niz in [' V1', ' V2', ' V3', ' V', ' SEM']:
        predmet = predmet.replace(niz, '')
    return predmet

for urnik in Table(OSNOVA + 'urn', encoding='cp852'):
    for letnik in urnik.Letnik.split():
        if letnik not in SMERI:
            SMERI[letnik] = (letnik, None)
            print(letnik, urnik)
PREDMETI = {izlusci_predmet(urnik.Predmet) for urnik in Table(OSNOVA + 'urn', encoding='cp852')}
OSEBE = {izlusci_predmet(urnik.Profesor) for urnik in Table(OSNOVA + 'urn', encoding='cp852')}

ucilnice = {}
for ucilnica in Table(OSNOVA + 'uci', encoding='cp852'):
    pk = ucilnica.Predavalnica
    oznaka = ucilnica.Predavalnica
    velikost = ucilnica.Velikost
    racunalniska = ucilnica.Predavalnica[:3] == '3.1'
    cur = con.execute('''
        INSERT INTO
        ucilnica
        (oznaka, velikost, racunalniska)
        VALUES (?, ?, ?)
    ''', (oznaka, velikost, racunalniska))
    ucilnice[pk] = cur.lastrowid

letniki = {}
for oznaka in SMERI:
    pk = oznaka
    smer = SMERI[oznaka][0]
    leto = SMERI[oznaka][1]
    cur = con.execute('''
        INSERT INTO
        letnik
        (smer, leto)
        VALUES (?, ?)
    ''', (smer, leto))
    letniki[pk] = cur.lastrowid

predmeti = {}
for predmet in PREDMETI:
    pk = predmet
    ime = predmet
    kratica = predmet
    stevilo_studentov = 40
    racunalniski = False
    cur = con.execute('''
        INSERT INTO
        predmet
        (ime, kratica, stevilo_studentov, racunalniski)
        VALUES (?, ?, ?, ?)
    ''', (ime, kratica, stevilo_studentov, racunalniski))
    predmeti[pk] = cur.lastrowid

osebe = {}
for oseba in OSEBE:
    pk = oseba
    ime = '???'
    priimek = oseba
    email = None
    cur = con.execute('''
        INSERT INTO
        oseba
        (ime, priimek, email)
        VALUES (?, ?, ?)
    ''', (ime, priimek, email))
    osebe[pk] = cur.lastrowid

# URNIK = OSNOVA + 'urn'  # Row(Dan=5, Ura=10, Predavalnica='2.05', Predmet='UVP', Profesor='Pretnar', Letnik='1N 1P', VIS=True)

con.commit()
