from collections import defaultdict

from django.db.models import Prefetch

from urnik.models import Termin, Rezervacija, Ucilnica, DNEVI, MIN_URA, MAX_URA


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
        print(self.ucilnice)
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

