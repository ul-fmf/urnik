import pypxlib
import sqlite3

################################################################################
# OSNOVNE NASTAVITVE
################################################################################

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
con.execute('PRAGMA foreign_keys = ON')
OSNOVA = '/Users/matija/Documents/urnik/uvoz/urnik 1617letni.'
################################################################################
# POMOŽNE FUNKCIJE
################################################################################

def nalozi_paradox(koncnica):
    OSNOVA = '/Users/matija/Documents/urnik/uvoz/urnik 1617letni.'
    return pypxlib.Table(OSNOVA + koncnica, encoding='cp852')

def izlusci_predmet(predmet):
    for niz in (' V1', ' V2', ' V3', ' V', ' SEM'):
        predmet = predmet.replace(niz, '')
    return predmet

def izlusci_tip(predmet):
    if any(tip in predmet for tip in (' V1', ' V2', ' V3', ' V')):
        return 'V'
    elif ' SEM' in predmet:
        return 'S'
    else:
        return 'P'

def izlusci_ucilnico(ucilnica):
    if ucilnica[0] == '(' and ucilnica[-1] == ')':
        return ucilnica[1:-1]
    else:
        return ucilnica

def opozorilo(niz):
    print(niz)

def zdruzi_ure(ure):
    # zdruzene_ure = set()
    # for dan, ura in sorted(ure):
    #     trajanje = 1
    #     while (dan, ura + trajanje) in ure:
    #         ure.remove((dan, ura + trajanje))
    #         trajanje += 1
    #     zdruzene_ure.add((dan, ura, trajanje))
    # return zdruzene_ure
    for dan, ura in ure:
        yield dan, ura, 1


################################################################################
# PRAZNJENJE BAZE
################################################################################

con.execute('DELETE FROM predmet_letnik')
con.execute('DELETE FROM srecanje')
con.execute('DELETE FROM letnik')
con.execute('DELETE FROM oseba')
con.execute('DELETE FROM predmet')
con.execute('DELETE FROM ucilnica')
con.execute('UPDATE sqlite_sequence SET seq = 0')

################################################################################
# BRANJE STARIH PODATKOV
################################################################################

ucilnice = {}
for ucilnica in nalozi_paradox('uci'):
    if ucilnica.Predavalnica == '4.27':
        continue
    ucilnice[ucilnica.Predavalnica] = {
        'oznaka': ucilnica.Predavalnica,
        'velikost': ucilnica.Velikost,
        'racunalniska': ucilnica.Predavalnica[:3] == '3.1',
    }
NEZNANE_UCILNICE = {izlusci_ucilnico(urnik.Predavalnica) for urnik in nalozi_paradox('urn')}
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

OSEBE = {izlusci_predmet(urnik.Profesor) for urnik in nalozi_paradox('urn')}
osebe = {}
for oseba in OSEBE:
    osebe[oseba] = {
        'ime': '???',
        'priimek': oseba,
        'email': None,
    }

PREDMETI = {izlusci_predmet(urnik.Predmet) for urnik in nalozi_paradox('urn')}
predmeti = {}
for predmet in PREDMETI:
    predmeti[predmet] = {
        'ime': predmet,
        'kratica': predmet,
        'stevilo_studentov': 40,
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
    ura = urnik.Ura
    bloki.setdefault((ucilnica, tip, ucitelj, predmet), set()).add((urnik.Dan, urnik.Ura))
srecanja = []
for (ucilnica, tip, ucitelj, predmet), ure in bloki.items():
    for dan, ura, trajanje in zdruzi_ure(ure):
        srecanja.append({
            'ucilnica': ucilnica,
            'tip': tip,
            'ucitelj': ucitelj,
            'predmet': predmet,
            'dan': dan,
            'ura': ura,
            'trajanje': trajanje,
        })

    # ure.append({
    #     'ura': urnik.Ura,
    #     'dan': urnik.Dan,
    #     'trajanje': 1
    # })



################################################################################
# PISANJE V BAZO
################################################################################

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
        (ucilnica, tip, ucitelj, predmet, dan, ura, trajanje)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ucilnica_pk[ucilnica],
        srecanje['tip'],
        oseba_pk[srecanje['ucitelj']],
        predmet_pk[srecanje['predmet']],
        srecanje['dan'],
        srecanje['ura'],
        srecanje['trajanje']
    ))

con.commit()
