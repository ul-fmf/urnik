import sqlite3

con = sqlite3.connect('urnik.sqlite3')


def seznam_ucilnic(velikost=0):
    seznam = []
    for ucilnica in con.execute('''
        SELECT oznaka, velikost
        FROM ucilnica
        WHERE velikost >= ?
        ORDER BY velikost DESC
        ''', [velikost]):
        seznam.append(ucilnica)
    return seznam
