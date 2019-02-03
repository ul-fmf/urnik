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


class IskalnikKonfliktov(object):
    """Zgradi strukturo, ki omogoca hitro iskanje prekrivanj glede na datum in učilnico."""

    def __init__(self, ucilnice):
        self.ucilnice = set(ucilnice)
        self.zasedenost_ucilnic = defaultdict(list)
        self.rezerviranost_ucilnic = defaultdict(list)

    def dodaj_srecanja(self, semestri):
        for s in Srecanje.objects.filter(semester__in=semestri, ucilnica__in=self.ucilnice
                                         ).select_related('semester', 'predmet', 'ucilnica'):
            for d in s.dnevi():
                self.zasedenost_ucilnic[s.ucilnica_id, d].append(s)

    def dodaj_rezervacije(self, rezervacije):
        for r in rezervacije:
            for u in r.ucilnice.all():
                for d in r.dnevi():
                    self.rezerviranost_ucilnic[u, d].append(r)

    @staticmethod
    def za_rezervacije(rezervacije: RezervacijaQuerySet):
        min_datum = datetime.date.max
        max_datum = datetime.date.min
        for r in rezervacije:
            if r.zacetek < min_datum:
                min_datum = r.zacetek
            if r.konec > max_datum:
                max_datum = r.konec

        prihodnji_semestri = Semester.objects.filter(do__gte=min_datum, od__lte=max_datum)
        ucilnice = set()
        semestri = set()
        for r in rezervacije:
            ucilnice.update(r.ucilnice.all())
            semestri.update(s for s in prihodnji_semestri if r.zacetek <= s.do and s.od <= r.konec)

        iskalnik = IskalnikKonfliktov(ucilnice)
        iskalnik.dodaj_srecanja(semestri)
        iskalnik.dodaj_rezervacije(rezervacije)
        return iskalnik

    def konflikti_z_rezervacijo(self, r: Rezervacija):
        dnevi = defaultdict(lambda: namedtuple('Konfikt', ['srecanja', 'rezervacije'], defaults=([], []))())
        for u in r.ucilnice.all():
            if u not in self.ucilnice:
                raise ValueError("Struktura iskanja ni bila pripravljena za iskanje konfliktov v učinici {}".format(u))
            for d in r.dnevi():
                for s in self.zasedenost_ucilnic[u, d]:
                    if r.se_po_urah_prekriva(s.od, s.do):
                        dnevi[d].srecanja.append(s)
                for r2 in self.rezerviranost_ucilnic[u, d]:
                    if r2 != r and r.se_po_urah_prekriva(r2.od, r2.do):
                        dnevi[d].rezervacije.append(r2)
        return dict(dnevi)
