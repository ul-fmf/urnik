import sqlite3

con = sqlite3.connect('urnik.sqlite3')
con.row_factory = sqlite3.Row


def vprasaji(seznam):
    return ', '.join('?' for _ in seznam)

def seznam_ucilnic(velikost=0):
    sql = '''
        SELECT id, oznaka, velikost, racunalniska
        FROM ucilnica
        WHERE velikost >= ?
        ORDER BY oznaka
    '''
    return list(con.execute(sql, [velikost]))


def seznam_oseb():
    sql = '''
        SELECT id, ime, priimek, email
        FROM oseba
        ORDER BY priimek, ime
    '''
    return list(con.execute(sql))


def seznam_letnikov():
    sql = '''
        SELECT id, smer, leto, stevilo_studentov
        FROM letnik
        ORDER BY smer, leto
    '''
    return list(con.execute(sql))


def oseba(oseba):
    sql = '''
        SELECT id, ime, priimek, email
        FROM oseba
        WHERE id = ?
    '''
    return con.execute(sql, [oseba]).fetchone()


def uredi_osebo(oseba, ime, priimek, email):
    sql = '''
        UPDATE oseba
        SET ime = ?, priimek = ?, email = ?
        WHERE id = ?
    '''
    con.execute(sql, [ime, priimek, email, oseba])
    con.commit()


def ucilnica(ucilnica):
    sql = '''
        SELECT id, oznaka, velikost, racunalniska
        FROM ucilnica
        WHERE id = ?
    '''
    return con.execute(sql, [ucilnica]).fetchone()


def uredi_ucilnico(ucilnica, oznaka, velikost, racunalniska):
    sql = '''
        UPDATE ucilnica
        SET oznaka = ?, velikost = ?, racunalniska = ?
        WHERE id = ?
    '''
    con.execute(sql, [oznaka, velikost, racunalniska, ucilnica])
    con.commit()


def letnik(letnik):
    sql = '''
        SELECT id, smer, leto, stevilo_studentov
        FROM letnik
        WHERE id = ?
    '''
    return con.execute(sql, [letnik]).fetchone()


def uredi_letnik(letnik, smer, leto, stevilo_studentov):
    sql = '''
        UPDATE letnik
        SET smer = ?, leto = ?, stevilo_studentov = ?
        WHERE id = ?
    '''
    con.execute(sql, [smer, leto, stevilo_studentov, letnik])
    con.commit()


def urnik(letniki, osebe, ucilnice):
    sql = '''
        SELECT dan,
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
    '''.format(vprasaji(letniki), vprasaji(osebe), vprasaji(ucilnice))
    srecanja = [dict(srecanje) for srecanje in con.execute(sql, letniki + osebe + ucilnice)]
    return nastavi_sirine_srecanj(srecanja)

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
        prekrivanja_v_terminu = prekrivanja.get((ucilnica, dan, ura), [])
        prekrivanja_v_terminu.append(prvo)
        prekrivanja_v_terminu.append(drugo)
        prekrivanja[(ucilnica, dan, ura)] = prekrivanja_v_terminu
    return prekrivanja


def proste_ucilnice():
    '''Vrne podatke o vseh prostih učilnicah.

    Funkcija vrne slovar, ki paru (dan, ura) priredi seznam ID-jev
    učilnic, ki so takrat proste. Če prostih učilnic ni, se par (dan, ura)
    v slovarju ne pojavi.
    '''
    return {
        (1, 10): [6],
        (3, 8): [1, 2, 3]
    }


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
