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

def nalozi_podatke(tabela, kljuci=(), ime_kljuca='id', vrstni_red=()):
    where = 'WHERE {} IN ({})'.format(ime_kljuca, vprasaji(kljuci)) if kljuci else ''
    order_by = 'ORDER BY {}'.format(', '.join(vrstni_red)) if vrstni_red else ''
    sql = 'SELECT * FROM {} {} {}'.format(tabela, where, order_by)
    return OrderedDict(
        (vrstica[ime_kljuca], dict(vrstica)) for vrstica in con.execute(sql, kljuci)
    )

def poberi_edinega(slovarji):
    assert len(slovarji) == 1
    return list(slovarji.values())[0]



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

    for predmet in predmeti.values():
        predmet['opis_letnikov'] = '; '.join(
            ('{}, {}. letnik'.format(letniki[letnik]['smer'], letniki[letnik]['leto'])
            if
            letniki[letnik]['leto']
            else
            letniki[letnik]['smer'])
            for
            letnik
            in
            predmet.get('letniki', [])
        )


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
    return poberi_edinega(podatki_letnikov([kljuc]))

def podatki_osebe(kljuc):
    return poberi_edinega(podatki_oseb([kljuc]))

def podatki_ucilnic(kljuci=[]):
    return nalozi_podatke('ucilnica', kljuci, vrstni_red=('skrita', 'oznaka'))

def podatki_ucilnice(kljuc):
    return poberi_edinega(podatki_ucilnic([kljuc]))

def podatki_predmeta(kljuc):
    return poberi_edinega(podatki_predmetov([kljuc]))

def podatki_srecanja(kljuc):
    return poberi_edinega(podatki_srecanj([kljuc]))

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


def uredi_srecanje(srecanje, ucitelj, predmet, tip, oznaka):
    sql = '''
        UPDATE srecanje
        SET ucitelj = ?, predmet = ?, tip = ?, oznaka = ?
        WHERE id = ?
    '''
    con.execute(sql, [ucitelj, predmet, tip, oznaka, srecanje])
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
    srecanje = podatki_srecanja(id_srecanja)
    sql = '''
        INSERT INTO srecanje
        (ucitelj, ucilnica, predmet, ura, dan, trajanje, tip)
        VALUES
        (?, ?, ?, ?, ?, ?, ?)'''
    con.execute(sql, [srecanje['ucitelj']['id'], srecanje['ucilnica']['id'], srecanje['predmet']['id'],
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
        SET dan = NULL, ura = NULL
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
    pod_srecanj = podatki_srecanj()
    return {
        (ucilnica, dan, ura): [pod_srecanj[srecanje] for srecanje in srecanja]
        for
        (ucilnica, dan, ura), srecanja in prekrivanja.items()
    }

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
    pod_srecanj = podatki_srecanj()
    return {
        (ucilnica, dan, ura): [pod_srecanj[srecanje] for srecanje in srecanja]
        for
        (ucilnica, dan, ura), srecanja in prekrivanja.items()
    }

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
    pod_srecanj = podatki_srecanj()
    return {
        (letnik, dan, ura): [pod_srecanj[srecanje] for srecanje in srecanja]
        for
        (letnik, dan, ura), srecanja in prekrivanja.items()
    }

def prekrivanja():
    prekrivanja = {}
    for (ucilnica, dan, ura), srecanja in prekrivanje_ucilnic().items():
        prekrivanja.setdefault((dan, ura), {}).setdefault('ucilnice', {})[ucilnica] = srecanja
    for (letnik, dan, ura), srecanja in prekrivanje_letnikov().items():
        prekrivanja.setdefault((dan, ura), {}).setdefault('letniki', {})[letnik] = srecanja
    for (oseba, dan, ura), srecanja in prekrivanje_oseb().items():
        prekrivanja.setdefault((dan, ura), {}).setdefault('osebe', {})[oseba] = srecanja
    return OrderedDict(((dan, ura), prekrivanja[(dan, ura)]) for (dan, ura) in sorted(prekrivanja))

##########################################################################
# PRIKAZ URNIKA
##########################################################################

def urnik(letniki, osebe, predmeti, ucilnice, skrij_rezervacije=False):
    sql = '''
        SELECT DISTINCT srecanje.id
          FROM srecanje
               LEFT JOIN
               predmet_letnik ON srecanje.predmet = predmet_letnik.predmet
               LEFT JOIN
               slusatelji ON srecanje.predmet = slusatelji.predmet
         WHERE dan IS NOT NULL AND ura IS NOT NULL
            AND (predmet_letnik.letnik IN ({})
            OR srecanje.ucitelj IN ({})
            OR srecanje.predmet IN ({})
            OR srecanje.ucilnica IN ({})
            OR slusatelji.oseba in ({}))
         ORDER BY dan, ura, trajanje
    '''.format(vprasaji(letniki), vprasaji(osebe), vprasaji(predmeti), vprasaji(ucilnice), vprasaji(osebe))
    srecanja = podatki_srecanj([vrstica['id'] for vrstica in con.execute(sql, letniki + osebe + predmeti + ucilnice + osebe)])
    if skrij_rezervacije:
        srecanja = [srecanje for srecanje in srecanja.values() if srecanje['predmet']['kratica'] != 'REZ']
    else:
        srecanja = srecanja.values()
    return nastavi_sirine_srecanj(srecanja)

def fiziki():
    FIZIKALNE_UCILNICE = (
        'F1', 'F2', 'F3', 'F4', 'F5', 'F7',
        'P.01', 'P.03', 'P.04',
        'MFP', 'VFP'
    )
    FIZIKALNE_SMERI = ('Fiz',)
    sql = '''
        SELECT id FROM ucilnica WHERE oznaka in ({})
    '''.format(vprasaji(FIZIKALNE_UCILNICE))
    fizikalne_ucilnice = [
        vrstica['id'] for vrstica in con.execute(sql, FIZIKALNE_UCILNICE)
    ]
    sql = '''
        SELECT id FROM letnik WHERE smer in ({})
    '''.format(vprasaji(FIZIKALNE_SMERI))
    fizikalni_letniki = [
        vrstica['id'] for vrstica in con.execute(sql, FIZIKALNE_SMERI)
    ]
    return urnik(fizikalni_letniki, [], [], fizikalne_ucilnice)

def odlozena_srecanja():
    sql = '''
        SELECT id FROM srecanje
         WHERE dan IS NULL AND ura IS NULL
    '''
    odlozena = [vrstica['id'] for vrstica in con.execute(sql)]
    if odlozena:
        return podatki_srecanj(odlozena).values()
    else:
        return []

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
    return urnik(letniki, [ucitelj], [], [], skrij_rezervacije=True)


def ustrezne_ucilnice(stevilo_studentov):
    ucilnice = []
    for ucilnica in podatki_ucilnic().values():
        velikost = ucilnica['velikost']
        if velikost is None:
            continue
        elif not stevilo_studentov or 2/3 <= velikost / stevilo_studentov <= 3/4:
            ucilnica['ustreznost'] = 'morebiti'
            ucilnice.append(ucilnica)
        elif 3/4 < velikost / stevilo_studentov:
            ucilnica['ustreznost'] = 'ustrezna'
            ucilnice.append(ucilnica)
        else:
            continue
    return ucilnice

from copy import deepcopy

def oznaci_zasedenost(izbrano_srecanje, ucilnice):
    sql = '''
        SELECT dan,
               ura,
               trajanje,
               ucilnica
          FROM srecanje
         WHERE id != ? AND dan IS NOT NULL and ura IS NOT NULL AND ucilnica IN ({})
    '''.format(vprasaji(ucilnice))
    zasedene = {}
    for zasedenost in con.execute(sql, [izbrano_srecanje['id']] + [ucilnica['id'] for ucilnica in ucilnice]):
        dan = zasedenost['dan']
        for ura in range(zasedenost['ura'], zasedenost['ura'] + zasedenost['trajanje']):
            zasedene.setdefault((dan, ura), set()).add(zasedenost['ucilnica'])

    def prosta(ucilnica, dan, ura):
        return ucilnica['id'] not in zasedene.get((dan, ura), [])

    termini = {}
    for dan in range(1, 6):
        for zacetek in range(7, 20 - izbrano_srecanje['trajanje'] + 1):
            termin = termini.setdefault((dan, zacetek), {
                'ucilnice': deepcopy(ucilnice),
                'zasedenost': 'zaseden'
            })
            ure = range(zacetek, zacetek + izbrano_srecanje['trajanje'])
            proste_prave = False
            deloma_prave = False
            proste_alternative = False
            deloma_alternative = False
            for ucilnica in termin['ucilnice']:
                if all(prosta(ucilnica, dan, ura) for ura in ure):
                    ucilnica['zasedenost'] = 'prosta'
                    if ucilnica['ustreznost'] == 'ustrezna':
                        proste_prave = True
                    else:
                        proste_alternative = True
                elif any(prosta(ucilnica, dan, ura) for ura in ure):
                    ucilnica['zasedenost'] = 'deloma_prosta'
                    if ucilnica['ustreznost'] == 'ustrezna':
                        deloma_prave = True
                    else:
                        deloma_alternative = True
                else:
                    ucilnica['zasedenost'] = 'zasedena'
            if proste_prave:
                termin['zasedenost'] = 'prosto'
            elif deloma_prave and proste_alternative:
                termin['zasedenost'] = 'proste_le_alternative'
            elif deloma_prave and deloma_alternative:
                termin['zasedenost'] = 'vse_mogoce'
            elif deloma_prave:
                termin['zasedenost'] = 'deloma'
            elif proste_alternative:
                termin['zasedenost'] = 'proste_alternative'
            elif deloma_alternative:
                termin['zasedenost'] = 'deloma_proste_alternative'

    #     elif termin['deloma_proste'] and termin['proste_alternative']:
    #         termin['zasedenost'] = 'vsemogoce'
    #     elif termin['deloma_proste']:
    #         termin['zasedenost'] = 'deloma'
    #     elif termin['proste_alternative']:
    #         termin['zasedenost'] = 'proste_alternative'
    #     elif termin['deloma_proste_alternative']:
    #         termin['zasedenost'] = 'deloma_proste_alternative'
    #     else:
    #         termin['zasedenost'] = 'zaseden'


    return termini


def prosti_termini(id_srecanja):
    izbrano_srecanje = podatki_srecanja(id_srecanja)
    predmet = izbrano_srecanje['predmet']
    ucilnice = ustrezne_ucilnice(predmet['stevilo_studentov'])
    ucilnice = oznaci_zasedenost(izbrano_srecanje, ucilnice)
    return ucilnice

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
