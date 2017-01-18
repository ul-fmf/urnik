import sqlite3


################################################################################
# POMOŽNE DEFINICIJE
################################################################################

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row


def vprasaji(seznam):
    return ', '.join('?' for _ in seznam)


def seznam_slovarjev(vrstice):
    return [dict(vrstica) for vrstica in vrstice]

################################################################################
# NALAGANJE SEZNAMA
################################################################################


def seznam_letnikov():
    sql = '''
        SELECT id, smer, leto, stevilo_studentov
        FROM letnik
        ORDER BY smer, leto
    '''
    return seznam_slovarjev(con.execute(sql))


def seznam_oseb():
    sql = '''
        SELECT id, ime, priimek, email
        FROM oseba
        ORDER BY priimek, ime
    '''
    return seznam_slovarjev(con.execute(sql))


def seznam_ucilnic():
    sql = '''
        SELECT id, oznaka, velikost, racunalniska
        FROM ucilnica
        ORDER BY oznaka
    '''
    return seznam_slovarjev(con.execute(sql))

################################################################################
# UREJANJE
################################################################################


def uredi_letnik(letnik, smer, leto, stevilo_studentov):
    sql = '''
        UPDATE letnik
        SET smer = ?, leto = ?, stevilo_studentov = ?
        WHERE id = ?
    '''
    con.execute(sql, [smer, leto, stevilo_studentov, letnik])
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

################################################################################
# USTVARJANJE
################################################################################


def ustvari_letnik(smer, leto, stevilo_studentov):
    sql = '''
        INSERT INTO letnik
        (smer, leto, stevilo_studentov)
        VALUES
        (?, ?, ?)
    '''
    con.execute(sql, [smer, leto, stevilo_studentov])
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
    sql = '''
        SELECT id, smer, leto, stevilo_studentov
        FROM letnik
        WHERE id = ?
    '''
    return dict(con.execute(sql, [letnik]).fetchone())


def oseba(oseba):
    sql = '''
        SELECT id, ime, priimek, email
        FROM oseba
        WHERE id = ?
    '''
    return dict(con.execute(sql, [oseba]).fetchone())


def ucilnica(ucilnica):
    sql = '''
        SELECT id, oznaka, velikost, racunalniska
        FROM ucilnica
        WHERE id = ?
    '''
    return dict(con.execute(sql, [ucilnica]).fetchone())


def nalozi_srecanje(srecanje_id):
    sql_srecanje = '''
        SELECT id, ucitelj, ucilnica, ura, dan, trajanje, tip
        FROM srecanje
        WHERE id = ?
    '''
    srecanje = dict(con.execute(sql_srecanje, [srecanje_id]).fetchone())
    sql_letniki = '''
        SELECT letnik
        FROM letnik_srecanje
        WHERE srecanje = ?
    '''
    srecanje['letniki'] = [
        row['letnik'] for row in con.execute(sql_letniki, [srecanje_id]).fetchall()
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
        (ucitelj, ucilnica, ura, dan, trajanje, tip)
        VALUES
        (?, ?, ?, ?, ?, ?)'''
    cur = con.execute(sql, [srecanje['ucitelj'], srecanje['ucilnica'], srecanje['ura'],
                            srecanje['dan'], srecanje['trajanje'], srecanje['tip']])
    nov_id = cur.lastrowid
    for letnik in srecanje['letniki']:
        sql = '''INSERT INTO letnik_srecanje (letnik, srecanje) VALUES (?, ?)'''
        con.execute(sql, [letnik, nov_id])
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
        SELECT srecanje.id as id,
               dan,
               ura,
               trajanje,
               srecanje.ucitelj as ucitelj,
               oseba.priimek as priimek_ucitelja,
               srecanje.ucilnica as ucilnica,
               ucilnica.oznaka as oznaka_ucilnice
          FROM srecanje
               INNER JOIN
               oseba ON srecanje.ucitelj = oseba.id
               INNER JOIN
               ucilnica ON srecanje.ucilnica = ucilnica.id
               INNER JOIN
               letnik_srecanje ON srecanje.id = letnik_srecanje.srecanje
         WHERE letnik_srecanje.letnik IN ({})
            OR srecanje.ucitelj IN ({})
            OR srecanje.ucilnica IN ({})
         ORDER BY dan, ura, trajanje
    '''.format(vprasaji(letniki), vprasaji(osebe), vprasaji(ucilnice))
    srecanja = seznam_slovarjev(con.execute(sql, letniki + osebe + ucilnice))
    return nastavi_sirine_srecanj(srecanja)


def povezana_srecanja(srecanje):
    sql_letniki = '''
        SELECT letnik FROM letnik_srecanje WHERE srecanje = ?
    '''
    letniki = [row['letnik'] for row in con.execute(sql_letniki, [srecanje])]
    sql_ucitelj = '''
        SELECT ucitelj FROM srecanje WHERE id = ?
    '''
    ucitelj = con.execute(sql_ucitelj, [srecanje]).fetchone()['ucitelj']
    return urnik(letniki, [ucitelj], [])


def prosti_termini(id_srecanja, ustrezne=[9, 10], alternative=[6, 7, 8]):
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

    izbrano_srecanje = nalozi_srecanje(id_srecanja)

    termini = {}
    for dan in range(1, 6):
        for zacetek in range(7, 20 - izbrano_srecanje['trajanje'] + 1):
            termin = termini.setdefault((dan, zacetek), {
                'proste': set(),
                'deloma_proste': set(),
                'proste_alternative': set(),
            })
            ure = range(zacetek, zacetek + izbrano_srecanje['trajanje'])
            for ucilnica in ustrezne:
                if all(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['proste'].add(ucilnica)
                elif any(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['deloma_proste'].add(ucilnica)
            for ucilnica in alternative:
                if all(prosta(ucilnica, dan, ura) for ura in ure):
                    termin['proste_alternative'].add(ucilnica)

    for termin in termini.values():
        if termin['proste']:
            termin['zasedenost'] = 'prosto'
        elif termin['deloma_proste'] and termin['proste_alternative']:
            termin['zasedenost'] = 'deloma alternative'
        elif termin['deloma_proste']:
            termin['zasedenost'] = 'deloma'
        elif termin['proste_alternative']:
            termin['zasedenost'] = 'alternative'
        else:
            termin['zasedenost'] = ''
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
