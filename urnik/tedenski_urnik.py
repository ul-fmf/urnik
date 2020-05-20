import datetime
from typing import List, Set

from urnik.models import Termin, ENOTA_SIRINE, ENOTA_VISINE, MIN_URA, Srecanje, Rezervacija


class TedenskiUrnikTermin(Termin):
    REZERVACIJA = 'r'
    SRECANJE = 's'

    def __init__(self, dan, ura, trajanje, tip, model):
        super().__init__(dan, ura)
        self.tip = tip
        self.model = model
        self.trajanje = trajanje
        self.sirina = None
        self.zamik = None
        self.leftmost = False
        self.rightmost = False
        self.kategorije: Set[int] = set()  # hrani indekse različnih kategorij iz legende, ki jim srečanje pripada

    def __str__(self):
        return "Termin {} v dnevu {}, {}-{}, kategorije: {}".format(self.tip, self.dan, self.ura, self.ura+self.trajanje, self.kategorije)

    def __lt__(self, other):
        return (self.dan, self.ura, self.trajanje) < (other.dan, other.ura, other.trajanje)

    @classmethod
    def iz_srecanja(cls, s: Srecanje):
        return TedenskiUrnikTermin(s.dan, s.ura, s.trajanje, cls.SRECANJE, s)

    @classmethod
    def iz_rezervacije(cls, r: Rezervacija, d):
        return TedenskiUrnikTermin(d, r.od, r.trajanje, cls.REZERVACIJA, r)

    def je_srecanje(self):
        return self.tip == TedenskiUrnikTermin.SRECANJE

    def je_rezervacija(self):
        return self.tip == TedenskiUrnikTermin.REZERVACIJA

    def ime_za_prikaz(self):
        if self.tip == TedenskiUrnikTermin.SRECANJE:
            if (self.sirina >= 0.5 and len(self.model.predmet.ime) < 45 and self.trajanje > 1) or self.sirina == 1:
                return self.model.predmet.ime
            else:
                return self.model.predmet.kratica
        elif self.tip == TedenskiUrnikTermin.REZERVACIJA:
            if (self.sirina >= 0.5 and len(self.model.opomba) < 30 and self.trajanje > 1) or self.sirina == 1:
                return "Rezervacija: {}".format(self.model.opomba)
            else:
                return "REZ: {}".format(self.model.opomba)

    def style(self):
        # ura in dan sta None pri odloženih srečanjih
        if self.dan and self.ura:
            if self.zamik is None or self.sirina is None:
                raise ValueError("Pred klicem style je potrebno izračunati širine.")
            left = (self.dan - 1 + self.zamik) * ENOTA_SIRINE
            top = (self.ura - MIN_URA) * ENOTA_VISINE
            height = self.trajanje * ENOTA_VISINE
            width = self.sirina * ENOTA_SIRINE
            return 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%};'.format(
                left, width, top, height)
        else:
            return ''

    def css_classes(self):
        classes = []
        if self.leftmost: classes.append('leftmost')
        if self.rightmost: classes.append('rightmost')
        return ' '.join(classes)


class TedenskiUrnik:
    """Urnik enega konkretnega ali abstraktnega tedna.

    Predstavlja mrežo petih dni in uztreznih ur.
    """
    def __init__(self):
        self._termini: List[TedenskiUrnikTermin] = []

    def dodaj_srecanja(self, srecanja):
        self._termini.extend(TedenskiUrnikTermin.iz_srecanja(s) for s in srecanja)

    def dodaj_rezervacije(self, rezervacije, teden):
        self._termini.extend(TedenskiUrnikTermin.iz_rezervacije(r, d.weekday()+1) for r in rezervacije for d in r.dnevi_med(teden, teden + datetime.timedelta(days=4)))

    def kategoriziraj(self, kategorije):
        """
        Kategorije so množice objektov (letnik, predmet, oseba, učilnica), na katere se lahko nanaša eno srečanje.

        Ta funkcija za vsako izmed srečanj izračuna, na katere izmed objektov iz množice `kategorije` se nanaša.
        To določa tudi barvo srečanja pri prikazu.

        Ta funkcija bi lahko bila bolj učinkovita, če bi kategorije gradili pri ustvarjanju srečaj.
        """
        if not kategorije:
            return
        for termin in self._termini:
            povezani_objekti = termin.model.povezani_objekti()
            for i, kategorija in enumerate(kategorije):
                if kategorija in povezani_objekti:
                    termin.kategorije.add(i)

    @staticmethod
    def _razdeli_po_dneh(termini):
        dnevi = {}
        for srecanje in termini:
            dnevi.setdefault(srecanje.dan, []).append(srecanje)
        return dnevi.values()

    @staticmethod
    def _razdeli_dan_na_bloke(termini):
        blok, konec_zadnjega_srecanja = [], None

        for termin in termini:
            # Če se naslednje srečanje začne za koncem vseh prejšnjih, zaključimo blok.
            if konec_zadnjega_srecanja is not None and termin.ura >= konec_zadnjega_srecanja:
                yield blok
                blok, konec_zadnjega_srecanja = [], None

            # Vstavimo v prvi stolpec, kjer je prostor. Če ga ni, dodamo novega.
            for stolpec in blok:
                if stolpec[-1].ura + stolpec[-1].trajanje <= termin.ura:
                    stolpec.append(termin)
                    break
            else:
                blok.append([termin])

            # Popravimo konec zadnjega srečanja.
            konec = termin.ura + termin.trajanje
            if konec_zadnjega_srecanja is None or konec > konec_zadnjega_srecanja:
                konec_zadnjega_srecanja = konec

        if blok:
            yield blok

    def nastavi_sirine(self):
        self._termini.sort()
        for srecanja_dneva in self._razdeli_po_dneh(self._termini):
            for blok in self._razdeli_dan_na_bloke(srecanja_dneva):
                for i, stolpec in enumerate(blok):
                    for termin in stolpec:
                        termin.sirina = 1 / len(blok)
                        termin.zamik = i / len(blok)
                        termin.leftmost = (i == 0)
                        termin.rightmost = (i == len(blok) - 1)

    def termini(self, kategorije=None):
        self.nastavi_sirine()
        self.kategoriziraj(kategorije)
        return self._termini
