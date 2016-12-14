import sqlite3

con = sqlite3.connect('urnik.sqlite3')


def seznam_ucilnic(velikost=0):
    sql = '''
        SELECT oznaka, velikost
        FROM ucilnica
        WHERE velikost >= ?
        ORDER BY velikost DESC
    '''
    return list(con.execute(sql, [velikost]))


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
