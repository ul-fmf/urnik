import datetime
from collections import defaultdict, namedtuple

from django.db.models import Prefetch

from urnik.models import Termin, Rezervacija, Ucilnica, DNEVI, MIN_URA, MAX_URA, Srecanje, Semester, RezervacijaQuerySet


class ProsteUcilniceTermin(Termin):
    HUE_PRAZEN = 120  # zelena
    HUE_POLN = 0  # rdeca

    def __init__(self, dan, ura, ustrezne_ucilnice, zasedene_ucilnice, rezervirane_ucilnice):
        super().__init__(dan, ura)
        zasedene_pks = {u.pk for u in zasedene_ucilnice}
        rezervirane_pks = {u.pk for u in rezervirane_ucilnice}
        # Vse ustrezne proste ucilnice.
        self.proste = [u for u in ustrezne_ucilnice if u.pk not in zasedene_pks and u.pk not in rezervirane_pks]
        # Vse ustrezne ucilnice, ki so pa zasedene, ker je tam stalno srečanje. Vrednosti so razlogi za zasedenost.
        self.zasedene = [(u, r) for u, r in zasedene_ucilnice.items() if u.pk not in rezervirane_pks]
        # Vse ustrezne ucilnice, ki so pa zasedene, ker so rezervirane. Vrednosti so razlogi za zasedenost.
        self.rezervirane = list(rezervirane_ucilnice.items())
        # ucilnice, ki bodo prikazane, skupaj s stanjem in razlogom
        self.prikazane_ucilnice = []

    def filtriraj_ucilnice(self, pokazi_zasedene):
        vse = [('prosta', u, None) for u in self.proste]
        if pokazi_zasedene:
            vse.extend([('rezervirana', u, r) for u, r in self.rezervirane])
            vse.extend([('zasedena', u, r) for u, r in self.zasedene])
        self.prikazane_ucilnice = sorted(vse, key=lambda x: x[1])

    def hue(self):
        h = self.HUE_PRAZEN if self.proste else self.HUE_POLN
        return "{:.0f}".format(h)


class ProsteUcilnice(object):
    """Zgradi strukturo, ki omogoca hitro iskanje prekrivanj za dane ucilnice glede na uro in dan v tednu."""
    def __init__(self, ucilnice):
        self.ucilnice = set(ucilnice)
        self.zasedenost_ucilnic = defaultdict(dict)
        self.rezerviranost_ucilnic = defaultdict(dict)

    def dodaj_srecanja_semestra(self, semester):
        for srecanje in semester.srecanja.select_related('ucilnica', 'predmet').prefetch_related('ucitelji'
                                       ).filter(ucilnica__in=[u.pk for u in self.ucilnice]).exclude(ura__isnull=True):
            for i in range(srecanje.trajanje):
                self.zasedenost_ucilnic[srecanje.dan, srecanje.ura + i][srecanje.ucilnica] = srecanje

    def upostevaj_rezervacije_za_teden(self, teden):
        self.upostevaj_rezervacije(Rezervacija.objects.v_tednu(teden))

    def upostevaj_rezervacije(self, rezervacije):
        for rezervacija in rezervacije.prefetch_related(
                Prefetch(
                    'ucilnice',
                    queryset=Ucilnica.objects.filter(pk__in=[u.pk for u in self.ucilnice]),
                    to_attr='ustrezne_ucilnice'),
                'osebe'):
            for ucilnica in rezervacija.ustrezne_ucilnice:
                for dan in rezervacija.dnevi():
                    for ura in range(rezervacija.od, rezervacija.do):
                        self.rezerviranost_ucilnic[dan.isoweekday(), ura][ucilnica] = rezervacija

    def dobi_termine(self):
        termini = [ProsteUcilniceTermin(d, u, self.ucilnice, self.zasedenost_ucilnic[d, u],
                                        self.rezerviranost_ucilnic[d, u])
                   for d in range(1, len(DNEVI) + 1) for u in range(MIN_URA, MAX_URA)]
        return termini


class Konflikt(object):
    def __init__(self):
        self.srecanja = []
        self.rezervacije = []

    @property
    def st_konfliktov(self):
        return len(self.srecanja) + len(self.rezervacije)

    def __bool__(self):
        return self.st_konfliktov > 0


class IskalnikKonfliktov(object):
    """Zgradi strukturo, ki omogoca hitro iskanje prekrivanj glede na datum in učilnico."""

    def __init__(self, ucilnice, min_datum, max_datum):
        self.ucilnice = set(ucilnice)
        self.min_datum = min_datum
        self.max_datum = max_datum
        self.zasedenost_ucilnic = defaultdict(list)
        self.rezerviranost_ucilnic = defaultdict(list)

    def dodaj_srecanja(self):
        self.dodaj_srecanja_semestrov(Semester.objects.v_obdobju(self.min_datum, self.max_datum))

    def dodaj_srecanja_semestrov(self, semestri):
        for s in Srecanje.objects.filter(semester__in=semestri, ucilnica__in=self.ucilnice
                                         ).exclude(ura__isnull=True).select_related('semester', 'predmet', 'ucilnica'):
            for d in s.dnevi_med(self.min_datum, self.max_datum):
                self.zasedenost_ucilnic[s.ucilnica_id, d].append(s)

    def dodaj_rezervacije(self, rezervacije):
        for r in rezervacije:
            for u in r.ucilnice.all():
                for d in r.dnevi_med(self.min_datum, self.max_datum):
                    self.rezerviranost_ucilnic[u, d].append(r)

    @staticmethod
    def za_rezervacije(rezervacije: RezervacijaQuerySet):
        min_datum = datetime.date.max
        max_datum = datetime.date.min
        ucilnice = set()
        for r in rezervacije:
            if r.zacetek < min_datum:
                min_datum = r.zacetek
            if r.konec > max_datum:
                max_datum = r.konec
            ucilnice.update(r.ucilnice.all())

        iskalnik = IskalnikKonfliktov(ucilnice, min_datum, max_datum)
        iskalnik.dodaj_srecanja()
        iskalnik.dodaj_rezervacije(rezervacije)
        return iskalnik

    def konflikti_z_rezervacijo(self, r: Rezervacija):
        for u in r.ucilnice.all():
            for d in r.dnevi():
                k = self.konflikti(u, d, r.od, r.do, r)
                if k:
                    yield u, d, k

    def konflikti(self, ucilnica, datum, od, do, ignore=None):
        """Vrne konflikte z dejavnostjo, ki bi v ucilnici `ucilnica` potekala dne `datum` od ure `od` do `do`."""
        konflikti = Konflikt()
        if ucilnica not in self.ucilnice:
            raise ValueError("Struktura iskanja ni bila pripravljena za iskanje konfliktov v učinici {}".format(ucilnica))
        if not (self.min_datum <= datum <= self.max_datum):
            raise ValueError("Struktura iskanja ni bila pripravljena za iskanje konfliktov dne {}".format(datum))

        for s in self.zasedenost_ucilnic[ucilnica, datum]:
            if s != ignore and s.se_po_urah_prekriva(od, do):
                konflikti.srecanja.append(s)

        for r in self.rezerviranost_ucilnic[ucilnica, datum]:
            if r != ignore and r.se_po_urah_prekriva(od, do):
                konflikti.rezervacije.append(r)

        return konflikti
