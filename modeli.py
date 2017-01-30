import sqlite3
from collections import OrderedDict

##########################################################################
# POMOŽNE DEFINICIJE
##########################################################################

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys = ON")


def vprasaji(seznam):
    return ', '.join('?' for _ in seznam)


def seznam_slovarjev(vrstice):
    return [dict(vrstica) for vrstica in vrstice]


def nalozi_podatke(tabela, kljuci=(), ime_kljuca='id', vrstni_red=()):
    where = 'WHERE {} IN ({})'.format(ime_kljuca, vprasaji(kljuci)) if kljuci else ''
    order_by = 'ORDER BY {}'.format(', '.join(vrstni_red)) if vrstni_red else ''
    sql = 'SELECT * FROM {} {} {}'.format(tabela, where, order_by)
    return OrderedDict(
        (vrstica[ime_kljuca], dict(vrstica)) for vrstica in con.execute(sql, kljuci)
    )

def nalozi_podatek(tabela, kljuc, ime_kljuca='id'):
    podatek = nalozi_podatke(tabela, kljuci=[kljuc], ime_kljuca=ime_kljuca)
    assert len(podatek) == 1
    return podatek[kljuc]



##########################################################################
# NALAGANJE PODATKOV
##########################################################################

def podatki_ucilnic(kljuci=[]):
    return nalozi_podatke('ucilnica', kljuci, vrstni_red=('oznaka',))

def podatki_letnikov(kljuci=[]):
    return nalozi_podatke('letnik', kljuci, vrstni_red=('smer', 'leto'))

def podatki_oseb(kljuci=[]):
    return nalozi_podatke('oseba', kljuci, vrstni_red=('priimek', 'ime'))

def podatki_predmetov(kljuci=[]):
    predmeti = nalozi_podatke('predmet', kljuci, vrstni_red=('ime',))
    sql_letniki = '''
        SELECT predmet, letnik FROM predmet_letnik
    '''
    if kljuci:
        sql_letniki += ' WHERE predmet IN ({})'.format(vprasaji(kljuci))
    povezani_letniki = set()
    for predmet, letnik in con.execute(sql_letniki, kljuci):
        predmeti[predmet].setdefault('letniki', set()).add(letnik)
        povezani_letniki.add(letnik)
    letniki = podatki_letnikov(list(povezani_letniki))
    sql_osebe = '''
        SELECT predmet, oseba FROM slusatelji
    '''
    if kljuci:
        sql_osebe += ' WHERE predmet IN ({})'.format(vprasaji(kljuci))
    povezane_osebe = set()
    for predmet, oseba in con.execute(sql_osebe, kljuci):
        predmeti[predmet].setdefault('slusatelji', set()).add(oseba)
        povezane_osebe.add(oseba)
    osebe = podatki_oseb(list(povezane_osebe))
    for predmet in predmeti.values():
        predmet['letniki'] = [
            letniki[letnik] for letnik in predmet.get('letniki', set())
        ]
        predmet['slusatelji'] = [
            osebe[oseba] for oseba in predmet.get('slusatelji', set())
        ]
    return predmeti

def podatki_srecanj(kljuci=[]):
    srecanja = nalozi_podatke('srecanje', kljuci, vrstni_red=('dan', 'ura'))
    sql = '''
        SELECT predmet, letnik FROM predmet_letnik WHERE predmet IN ({}) 
    '''.format(vprasaji(kljuci))
    povezani_predmeti = set()
    povezane_osebe = set()
    povezane_ucilnice = set()
    for srecanje in srecanja.values():
        povezani_predmeti.add(srecanje['predmet'])
        povezane_osebe.add(srecanje['ucitelj'])
        povezane_ucilnice.add(srecanje['ucilnica'])
    osebe = podatki_oseb(list(povezane_osebe))
    predmeti = podatki_predmetov(list(povezani_predmeti))
    ucilnice = podatki_ucilnic(list(povezane_ucilnice))
    for srecanje in srecanja.values():
        srecanje['ucitelj'] = osebe.get(srecanje['ucitelj'])
        srecanje['ucilnica'] = ucilnice.get(srecanje['ucilnica'])
        srecanje['predmet'] = predmeti.get(srecanje['predmet'])
    return srecanja

def podatki_letnika(kljuc):
    return nalozi_podatek('letnik', kljuc)

def podatki_osebe(kljuc):
    return nalozi_podatek('oseba', kljuc)

def podatki_ucilnic(kljuci=[]):
    return nalozi_podatke('ucilnica', kljuci, vrstni_red=('skrita', 'oznaka'))

def podatki_ucilnice(kljuc):
    return nalozi_podatek('ucilnica', kljuc)

# def podatki_srecanj(kljuci=[]):
#     return nalozi_podatke('srecanje', kljuci)

def podatki_predmeta(kljuc):
    predmet = nalozi_podatek('predmet', kljuc)
    sql = 'SELECT letnik FROM predmet_letnik WHERE predmet = ?'
    predmet['letniki'] = [vrstica['letnik'] for vrstica in con.execute(sql, (kljuc,))]
    return predmet

def seznam_predmetov():
    sql = '''SELECT * FROM predmet ORDER BY ime'''
    predmeti = seznam_slovarjev(con.execute(sql))
    sql = '''
        SELECT predmet, smer, leto
          FROM letnik
               INNER JOIN
               predmet_letnik ON predmet_letnik.letnik = letnik.id
    '''
    letniki_predmeta = {}
    for id_predmeta, smer, leto in con.execute(sql):
        letniki_predmeta.setdefault(id_predmeta, []).append((smer, leto))
    for predmet in predmeti:
        letniki = '; '.join(
            '{}, {}. letnik'.format(smer, leto)
            for
            smer, leto
            in
            letniki_predmeta.get(predmet['id'], [])
        )
        predmet['opis'] = '{} ({})'.format(
            predmet['ime'], letniki) if letniki else predmet['ime']
    return predmeti

##########################################################################
# UREJANJE
##########################################################################


def uredi_letnik(letnik, smer, leto):
    sql = '''
        UPDATE letnik
        SET smer = ?, leto = ?
        WHERE id = ?
    '''
    con.execute(sql, [smer, leto, letnik])
    con.commit()


def uredi_osebo(oseba, ime, priimek, email):
    sql = '''
        UPDATE oseba
        SET ime = ?, priimek = ?, email = ?
        WHERE id = ?
    '''
    con.execute(sql, [ime, priimek, email, oseba])
    con.commit()


def uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska, skrita):
    sql = '''
        UPDATE ucilnica
        SET oznaka = ?, velikost = ?, racunalniska = ?, skrita = ?
        WHERE id = ?
    '''
    con.execute(sql, [oznaka, velikost, racunalniska, ucilnica, skrita])
    con.commit()


def uredi_srecanje(srecanje, ucitelj, predmet, tip):
    sql = '''
        UPDATE srecanje
        SET ucitelj = ?, predmet = ?, tip = ?
        WHERE id = ?
    '''
    con.execute(sql, [ucitelj, predmet, tip, srecanje])
    con.commit()


def uredi_predmet(predmet, ime, kratica, stevilo_studentov, letniki):
    sql = '''
        UPDATE predmet
        SET ime = ?, kratica = ?, stevilo_studentov = ?
        WHERE id = ?
    '''
    con.execute(sql, [ime, kratica, stevilo_studentov, predmet])
    sql = '''
        DELETE FROM predmet_letnik
        WHERE predmet = ? AND letnik NOT IN ({})
    '''.format(vprasaji(letniki))
    con.execute(sql, [predmet] + letniki)
    sql = '''
        INSERT INTO predmet_letnik
        (predmet, letnik)
        SELECT ?, id
        FROM letnik
        WHERE id NOT in (SELECT letnik FROM predmet_letnik WHERE predmet = ?) AND id IN ({})
    '''.format(vprasaji(letniki))
    con.execute(sql, [predmet, predmet] + letniki)
    con.commit()


##########################################################################
# USTVARJANJE
##########################################################################


def ustvari_letnik(smer, leto):
    sql = '''
        INSERT INTO letnik
        (smer, leto)
        VALUES
        (?, ?)
    '''
    con.execute(sql, [smer, leto])
    con.commit()


def ustvari_osebo(ime, priimek, email):
    sql = '''
        INSERT INTO oseba
        (ime , priimek, email)
        VALUES
        (?, ?, ?)
    '''
    con.execute(sql, [ime, priimek, email])
    con.commit()


def ustvari_ucilnico(oznaka, velikost, racunalniska):
    sql = '''
        INSERT INTO ucilnica
        (oznaka, velikost, racunalniska)
        VALUES
        (?, ?, ?)
    '''
    con.execute(sql, [oznaka, velikost, racunalniska])
    con.commit()


def ustvari_predmet(ime, kratica, stevilo_studentov, letniki):
    sql = '''
        INSERT INTO predmet
        (ime, kratica, stevilo_studentov)
        VALUES
        (?, ?, ?)
    '''
    cur = con.execute(sql, [ime, kratica, stevilo_studentov])
    predmet = cur.lastrowid
    con.commit()
    uredi_predmet(predmet, ime, kratica, stevilo_studentov, letniki)

##########################################################################
# NALAGANJE POSAMEZNE ENTITETE
##########################################################################


def nalozi_predmet(predmet):
    sql = '''SELECT * FROM predmet WHERE id = ?'''
    return dict(con.execute(sql, [predmet]).fetchone())


def nalozi_srecanje(srecanje_id):
    sql_srecanje = '''
        SELECT id, predmet, ucitelj, ucilnica, ura, dan, trajanje, tip
        FROM srecanje
        WHERE id = ?
    '''
    srecanje = dict(con.execute(sql_srecanje, [srecanje_id]).fetchone())
    sql_letniki = '''
        SELECT letnik
        FROM predmet_letnik
        WHERE predmet = ?
    '''
    srecanje['letniki'] = [
        row['letnik'] for row in con.execute(sql_letniki, [srecanje['predmet']]).fetchall()
    ]
    return srecanje

##########################################################################
# UREJANJE SREČANJ
##########################################################################

def nastavi_trajanje(srecanje, trajanje):
    sql = '''
        UPDATE srecanje
        SET trajanje = ?
        WHERE id = ?
    '''
    con.execute(sql, [trajanje, srecanje])
    con.commit()


def izbrisi_srecanje(srecanje):
    sql = '''
        DELETE FROM srecanje
        WHERE id = ?
    '''
    con.execute(sql, [srecanje])
    con.commit()


def podvoji_srecanje(id_srecanja):
    srecanje = nalozi_srecanje(id_srecanja)
    sql = '''
        INSERT INTO srecanje
        (ucitelj, ucilnica, predmet, ura, dan, trajanje, tip)
        VALUES
        (?, ?, ?, ?, ?, ?, ?)'''
    con.execute(sql, [srecanje['ucitelj'], srecanje['ucilnica'], srecanje['predmet'],
                      srecanje['ura'], srecanje['dan'], srecanje['trajanje'], srecanje['tip']])
    con.commit()


def premakni_srecanje(srecanje, dan, ura, ucilnica):
    sql = '''
        UPDATE srecanje
        SET dan = ?, ura = ?, ucilnica = ?
        WHERE id = ?
    '''
    con.execute(sql, [dan, ura, ucilnica, srecanje])
    con.commit()


def odlozi_srecanje(srecanje):
    sql = '''
        UPDATE srecanje
        SET dan = NULL, ura = NULL, ucilnica = NULL
        WHERE id = ?
    '''
    con.execute(sql, [srecanje])
    con.commit()


##########################################################################
# IZRAČUN PREKRIVANJ
##########################################################################

def prekrivanje_ucilnic():
    '''Vrne podatke o prekrivanju srečanj po učilnicah.

    Funkcija vrne slovar, ki trojici (ID učilnice, dan, ura)
    priredi seznam ID-jev srečanj, ki tam in takrat potekajo hkrati.
    '''
    sql = '''
    SELECT prvo.ucilnica AS ucilnica,
           prvo.dan AS dan,
           drugo.ura AS ura,
           prvo.id AS prvo,
           drugo.id AS drugo
      FROM srecanje AS prvo
           INNER JOIN
           srecanje AS drugo ON prvo.ucilnica = drugo.ucilnica AND 
                                prvo.dan = drugo.dan
     WHERE prvo.id != drugo.id AND 
           prvo.ura <= drugo.ura AND 
           drugo.ura < prvo.ura + prvo.trajanje
    '''
    prekrivanja = {}
    for ucilnica, dan, ura, prvo, drugo in con.execute(sql):
        prekrivanja.setdefault((ucilnica, dan, ura), set()).update((prvo, drugo))
    return prekrivanja

def prekrivanje_oseb():
    sql = '''
    SELECT prvo.ucitelj AS oseba,
           prvo.dan AS dan,
           drugo.ura AS ura,
           prvo.id AS prvo,
           drugo.id AS drugo
      FROM srecanje AS prvo
           INNER JOIN
           srecanje AS drugo ON prvo.ucitelj = drugo.ucitelj AND 
                                prvo.dan = drugo.dan
     WHERE prvo.id != drugo.id AND 
           prvo.ura <= drugo.ura AND 
           drugo.ura < prvo.ura + prvo.trajanje
    '''
    prekrivanja = {}
    for ucitelj, dan, ura, prvo, drugo in con.execute(sql):
        prekrivanja.setdefault((ucitelj, dan, ura), set()).update((prvo, drugo))
    return prekrivanja

def prekrivanje_letnikov():
    sql = '''
    SELECT prvo_letnik.letnik AS letnik,
           prvo.dan AS dan,
           drugo.ura AS ura,
           prvo.id AS prvo,
           drugo.id AS drugo
      FROM srecanje AS prvo
           INNER JOIN
           predmet_letnik AS prvo_letnik ON prvo.predmet = prvo_letnik.predmet
           INNER JOIN
           predmet_letnik AS drugo_letnik ON prvo_letnik.letnik = drugo_letnik.letnik
           INNER JOIN
           srecanje AS drugo ON drugo.predmet = drugo_letnik.predmet AND prvo.dan = drugo.dan
     WHERE prvo.id != drugo.id AND 
           prvo.ura <= drugo.ura AND 
           drugo.ura < prvo.ura + prvo.trajanje
    '''
    prekrivanja = {}
    for letnik, dan, ura, prvo, drugo in con.execute(sql):
        prekrivanja.setdefault((letnik, dan, ura), set()).update((prvo, drugo))
    return prekrivanja

##########################################################################
# PRIKAZ URNIKA
##########################################################################

def urnik(letniki, osebe, predmeti, ucilnice):
    sql = '''
        SELECT DISTINCT srecanje.id
          FROM srecanje
               LEFT JOIN
               predmet_letnik ON srecanje.predmet = predmet_letnik.predmet
               LEFT JOIN
               slusatelji ON srecanje.predmet = slusatelji.predmet
         WHERE dan IS NOT NULL AND ucilnica IS NOT NULL AND ura IS NOT NULL
            AND (predmet_letnik.letnik IN ({})
            OR srecanje.ucitelj IN ({})
            OR srecanje.predmet IN ({})
            OR srecanje.ucilnica IN ({})
            OR slusatelji.oseba in ({}))
         ORDER BY dan, ura, trajanje
    '''.format(vprasaji(letniki), vprasaji(osebe), vprasaji(predmeti), vprasaji(ucilnice), vprasaji(osebe))
    srecanja = podatki_srecanj([vrstica['id'] for vrstica in con.execute(sql, letniki + osebe + predmeti + ucilnice + osebe)])
    bla = nastavi_sirine_srecanj(srecanja.values())
    print(bla)
    return bla

def odlozena_srecanja():
    sql = '''
        SELECT id FROM srecanje
         WHERE dan IS NULL AND ucilnica IS NULL AND ura IS NULL
    '''
    return podatki_srecanj([vrstica['id'] for vrstica in con.execute(sql)]).values()

def povezana_srecanja(srecanje):
    sql_letniki = '''
        SELECT letnik
          FROM predmet_letnik
               INNER JOIN
               srecanje ON predmet_letnik.predmet = srecanje.predmet
         WHERE srecanje.id = ?
    '''
    letniki = [row['letnik'] for row in con.execute(sql_letniki, [srecanje])]
    sql_ucitelj = '''
        SELECT ucitelj FROM srecanje WHERE id = ?
    '''
    ucitelj = con.execute(sql_ucitelj, [srecanje]).fetchone()['ucitelj']
    return urnik(letniki, [ucitelj], [], [])


def ustrezne_ucilnice(stevilo_studentov):
    ustrezne = []
    morebitne = []
    for ucilnica in podatki_ucilnic().values():
        velikost = ucilnica['velikost']
        if velikost is None:
            pass
        elif stevilo_studentov is None or 2/3 <= velikost / stevilo_studentov <= 3/4:
            morebitne.append(ucilnica['id'])
        elif 3/4 < velikost / stevilo_studentov:
            ustrezne.append(ucilnica['id'])
    return ustrezne, morebitne


def prosti_termini(id_srecanja):
    izbrano_srecanje = nalozi_srecanje(id_srecanja)
    predmet = nalozi_predmet(izbrano_srecanje['predmet'])
    podatki_uc = podatki_ucilnic()
    ustrezne, alternative = ustrezne_ucilnice(predmet['stevilo_studentov'])
    zasedene = {}
    ucilnice = ustrezne + alternative
    sql = '''
        SELECT dan,
               ura,
               trajanje,
               ucilnica
          FROM srecanje
         WHERE id != ? AND ucilnica IN ({})
    '''.format(vprasaji(ucilnice))
    for srecanje in con.execute(sql, [id_srecanja] + ucilnice):
        dan = srecanje['dan']
        for ura in range(srecanje['ura'], srecanje['ura'] + srecanje['trajanje']):
            zasedene.setdefault((dan, ura), set()).add(srecanje['ucilnica'])

    def prosta(ucilnica, dan, ura):
        return ucilnica not in zasedene.get((dan, ura), [])

    termini = {}
    for dan in range(1, 6):
        for zacetek in range(7, 20 - izbrano_srecanje['trajanje'] + 1):
            termin = {
                'proste': set(),
                'deloma_proste': set(),
                'proste_alternative': set(),
            }
            ure = range(zacetek, zacetek + izbrano_srecanje['trajanje'])
            for ucilnica in ustrezne:
                if all(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['proste'].add(ucilnica)
                elif any(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['deloma_proste'].add(ucilnica)
            for ucilnica in alternative:
                if all(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['proste_alternative'].add(ucilnica)
            if termin['proste'] or termin['deloma_proste'] or termin['proste_alternative']:
                termini[(dan, zacetek)] = termin

    for termin in termini.values():
        if termin['proste']:
            termin['zasedenost'] = 'prosto'
        elif termin['deloma_proste'] and termin['proste_alternative']:
            termin['zasedenost'] = 'deloma alternative'
        elif termin['deloma_proste']:
            termin['zasedenost'] = 'deloma'
        elif termin['proste_alternative']:
            termin['zasedenost'] = 'alternative'
        termin['ucilnice'] = [
            (podatki_uc[ucilnica], 'prosta') for ucilnica in termin['proste']
        ] + [
            (podatki_uc[ucilnica], 'prosta_alternativa') for ucilnica in termin['proste_alternative']
        ] + [
            (podatki_uc[ucilnica], 'deloma_prosta') for ucilnica in termin['deloma_proste']
        ]

    return termini


def razdeli_srecanja_po_dneh(srecanja):
    dnevi = {}
    for srecanje in srecanja:
        dnevi.setdefault(srecanje['dan'], []).append(srecanje)
    return dnevi.values()


def razdeli_dan_na_skupine(srecanja):
    skupina, konec_zadnjega_srecanja = [], None

    for srecanje in srecanja:
        # Če se naslednje srečanje začne za koncem vseh prejšnjih, zaključimo
        # skupino.
        if konec_zadnjega_srecanja is not None and srecanje['ura'] >= konec_zadnjega_srecanja:
            yield skupina
            skupina, konec_zadnjega_srecanja = [], None

        # Vstavimo v prvi stolpec, kjer je prostor. Če ga ni, dodamo novega.
        for stolpec in skupina:
            if stolpec[-1]['ura'] + stolpec[-1]['trajanje'] <= srecanje['ura']:
                stolpec.append(srecanje)
                break
        else:
            skupina.append([srecanje])

        # Popravimo konec zadnjega srečanja.
        konec = srecanje['ura'] + srecanje['trajanje']
        if konec_zadnjega_srecanja is None or konec > konec_zadnjega_srecanja:
            konec_zadnjega_srecanja = konec

    if skupina:
        yield skupina


def nastavi_sirine_srecanj(srecanja):
    for srecanja_dneva in razdeli_srecanja_po_dneh(srecanja):
        for skupina in razdeli_dan_na_skupine(srecanja_dneva):
            for i, stolpec in enumerate(skupina):
                for srecanje in stolpec:
                    srecanje['sirina'] = 1 / len(skupina)
                    srecanje['zamik'] = i / len(skupina)
    return srecanja
