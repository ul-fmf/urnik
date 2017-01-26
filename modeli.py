import sqlite3


################################################################################
# POMOŽNE DEFINICIJE
################################################################################

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys = ON")


def vprasaji(seznam):
    return ', '.join('?' for _ in seznam)


def seznam_slovarjev(vrstice):
    return [dict(vrstica) for vrstica in vrstice]

################################################################################
# SEZNAMI ENTITET
################################################################################


def seznam_letnikov():
    sql = '''SELECT * FROM letnik ORDER BY smer, leto'''
    return seznam_slovarjev(con.execute(sql))


def seznam_oseb():
    sql = '''SELECT * FROM oseba ORDER BY priimek, ime'''
    return seznam_slovarjev(con.execute(sql))


def seznam_ucilnic():
    sql = '''SELECT * FROM ucilnica ORDER BY oznaka'''
    return seznam_slovarjev(con.execute(sql))

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
        predmet['opis'] = '{} ({})'.format(predmet['ime'], letniki) if letniki else predmet['ime']
    return predmeti

################################################################################
# UREJANJE
################################################################################


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


def uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska):
    sql = '''
        UPDATE ucilnica
        SET oznaka = ?, velikost = ?, racunalniska = ?
        WHERE id = ?
    '''
    con.execute(sql, [oznaka, velikost, racunalniska, ucilnica])
    con.commit()

def uredi_srecanje(srecanje, ucitelj, predmet, tip):
    sql = '''
        UPDATE srecanje
        SET ucitelj = ?, predmet = ?, tip = ?
        WHERE id = ?
    '''
    con.execute(sql, [ucitelj, predmet, tip, srecanje])
    con.commit()

################################################################################
# USTVARJANJE
################################################################################


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

################################################################################
# NALAGANJE POSAMEZNE ENTITETE
################################################################################


def letnik(letnik):
    sql = '''SELECT * FROM letnik WHERE id = ?'''
    return dict(con.execute(sql, [letnik]).fetchone())


def oseba(oseba):
    sql = '''SELECT * FROM oseba WHERE id = ?'''
    return dict(con.execute(sql, [oseba]).fetchone())


def ucilnica(ucilnica):
    sql = '''SELECT * FROM ucilnica WHERE id = ?'''
    return dict(con.execute(sql, [ucilnica]).fetchone())


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


################################################################################
# UREJANJE SREČANJ
################################################################################

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


################################################################################
# PRIKAZ URNIKA
################################################################################

def urnik(letniki, osebe, ucilnice):
    sql = '''
        SELECT DISTINCT srecanje.id as id,
               dan,
               ura,
               trajanje,
               tip,
               srecanje.ucitelj as ucitelj,
               oseba.priimek as priimek_ucitelja,
               srecanje.ucilnica as ucilnica,
               ucilnica.oznaka as oznaka_ucilnice,
               predmet.ime as ime_predmeta
          FROM srecanje
               LEFT JOIN
               oseba ON srecanje.ucitelj = oseba.id
               LEFT JOIN
               ucilnica ON srecanje.ucilnica = ucilnica.id
               LEFT JOIN
               predmet_letnik ON srecanje.predmet = predmet_letnik.predmet
               LEFT JOIN
               predmet ON srecanje.predmet = predmet.id
         WHERE predmet_letnik.letnik IN ({})
            OR srecanje.ucitelj IN ({})
            OR srecanje.ucilnica IN ({})
         ORDER BY dan, ura, trajanje
    '''.format(vprasaji(letniki), vprasaji(osebe), vprasaji(ucilnice))
    srecanja = seznam_slovarjev(con.execute(sql, letniki + osebe + ucilnice))
    return nastavi_sirine_srecanj(srecanja)


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
    return urnik(letniki, [ucitelj], [])


def ustrezne_ucilnice(stevilo_studentov, racunalniski):
    ustrezne = []
    alternative = []
    for ucilnica in seznam_ucilnic():
        if ucilnica['velikost'] >= stevilo_studentov:
            ustrezne.append(ucilnica['id'])
        elif ucilnica['velikost'] >= 0.75 * stevilo_studentov:
            alternative.append(ucilnica['id'])
    return ustrezne, alternative


def prosti_termini(id_srecanja):
    izbrano_srecanje = nalozi_srecanje(id_srecanja)
    predmet = nalozi_predmet(izbrano_srecanje['predmet'])
    ustrezne, alternative = ustrezne_ucilnice(predmet['stevilo_studentov'], predmet['racunalniski'])
    zasedene = {}
    ucilnice = ustrezne + alternative
    sql = '''
        SELECT dan,
               ura,
               trajanje,
               ucilnica
          FROM srecanje
         WHERE ucilnica IN ({})
    '''.format(vprasaji(ucilnice))
    for srecanje in con.execute(sql, ucilnice):
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
            (ucilnica, 'prosta') for ucilnica in termin['proste']
        ] + [
            (ucilnica, 'prosta_alternativa') for ucilnica in termin['proste_alternative']
        ] + [
            (ucilnica, 'deloma_prosta') for ucilnica in termin['deloma_proste']
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
        # Če se naslednje srečanje začne za koncem vseh prejšnjih, zaključimo skupino.
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
