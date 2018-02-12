import datetime
from collections import defaultdict
from copy import deepcopy
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from .layout import nastavi_sirine_srecanj, nastavi_barve

MIN_URA, MAX_URA = 7, 20
ENOTA_VISINE = 1 / (MAX_URA - MIN_URA)
DNEVI = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
ENOTA_SIRINE = 1 / len(DNEVI)


class OsebaQuerySet(models.QuerySet):

    def aktivni(self):
        slusatelji = self.filter(predmeti__isnull=False)
        ucitelji = self.filter(srecanja__isnull=False)
        return (slusatelji | ucitelji).distinct()


class Oseba(models.Model):
    ime = models.CharField(max_length=192)
    priimek = models.CharField(max_length=192)
    email = models.EmailField(blank=True)
    domaca_stran = models.CharField(max_length=192, blank=True)
    objects = OsebaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'osebe'
        default_related_name = 'osebe'
        ordering = ('priimek', 'ime')

    def __str__(self):
        if self.ime:
            return '{} {}'.format(self.ime, self.priimek)
        else:
            return self.priimek

    def vrstni_red(self):
        return self.priimek.replace('Č', 'Cz').replace('Š', 'Sz').replace('Ž', 'Zz')

    def vsa_srecanja(self, semester):
        return (self.srecanja.filter(semester=semester) | semester.srecanja.filter(predmet__slusatelji=self)).distinct()


class Letnik(models.Model):
    MATEMATIKA, FIZIKA = 'M', 'F'
    ODDELEK = (
        (MATEMATIKA, 'matematika'), (FIZIKA, 'fizika'),
    )
    oddelek = models.CharField(max_length=1, choices=ODDELEK, blank=True)
    smer = models.CharField(max_length=192)
    leto = models.CharField(max_length=192, null=True)
    kratica = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = 'letniki'
        default_related_name = 'letniki'
        ordering = ('oddelek', 'smer', 'leto')

    def __str__(self):
        if self.leto:
            return '{}, {}'.format(self.smer, self.leto)
        else:
            return self.smer

    def srecanja(self, semester):
        return semester.srecanja.filter(predmet__letniki=self).distinct()


class UcilnicaQuerySet(models.QuerySet):
    VELIKOST = [
        ('majhna', 'majhna'),
        ('obicajna', 'običajna'),
        ('velika', 'velika'),
    ]

    # TODO: fix this mess
    def ustrezne(self, tip, oddelek):
        if oddelek == 'MAT':
            obicajna = Ucilnica.MATEMATICNA
        else:
            obicajna = Ucilnica.FIZIKALNA
        if tip == 'velika':
            ustrezne = self.filter(tip=obicajna, velikost__gte=60)
            alternative = self.filter(velikost__gte=45)
        elif tip == 'obicajna':
            ustrezne = self.filter(tip=obicajna, velikost__gte=30, velikost__lt=60)
            alternative = self.filter(velikost__gte=24, velikost__lt=80)
        elif tip == 'majhna':
            ustrezne = self.filter(tip=obicajna, velikost__lt=30)
            alternative = self.filter(velikost__lt=40)
        elif tip == 'racunalniska':
            ustrezne = self.filter(tip=Ucilnica.RACUNALNISKA)
            alternative = self.none()
        elif tip == 'praktikum':
            ustrezne = self.filter(tip=Ucilnica.PRAKTIKUM)
            alternative = self.none()
        else:
            ustrezne = self.none()
            alternative = self.filter(velikost__isnull=True)

        return list(ustrezne), list(alternative.exclude(pk__in=ustrezne))

    def ustrezne_velikosti(self, velikosti):
        if not velikosti:
            return self.all()
        ustrezne = self.none()
        if 'majhna' in velikosti:
            ustrezne |= self.filter(velikost__lt=30)
        if 'obicajna' in velikosti:
            ustrezne |= self.filter(velikost__gte=30, velikost__lt=60)
        if 'velika' in velikosti:
            ustrezne |= self.filter(velikost__gte=60)
        return ustrezne

    def objavljene(self):
        return self.filter(tip__in=Ucilnica.OBJAVLJENI_TIPI)


class Ucilnica(models.Model):
    MATEMATICNA, FIZIKALNA, RACUNALNISKA = 'M', 'F', 'R'
    PRAKTIKUM, PISARNA, ZUNANJA = 'P', 'K', 'X'
    TIP = (
        (MATEMATICNA, 'matematična'), (FIZIKALNA, 'fizikalna'),
        (RACUNALNISKA, 'računalniška'), (PRAKTIKUM, 'praktikum'),
        (PISARNA, 'pisarna'), (ZUNANJA, 'zunanja'),
    )
    OBJAVLJENI_TIPI = (
        MATEMATICNA,
        FIZIKALNA,
        RACUNALNISKA,
        PRAKTIKUM,
    )

    tip = models.CharField(max_length=1, choices=TIP, default=ZUNANJA, blank=True)
    oznaka = models.CharField(max_length=192, unique=True)
    kratka_oznaka = models.CharField(max_length=10, blank=True)
    velikost = models.PositiveSmallIntegerField(blank=True, null=True)
    objects = UcilnicaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'ucilnice'
        default_related_name = 'ucilnice'
        ordering = ('oznaka',)

    def __str__(self):
        return self.oznaka

    def __lt__(self, other):
        return self.oznaka < other.oznaka

    def kratko_ime(self):
        if self.kratka_oznaka:
            return self.kratka_oznaka
        return self.oznaka


class Predmet(models.Model):
    ime = models.CharField(max_length=192)
    kratica = models.CharField(max_length=64)
    stevilo_studentov = models.PositiveSmallIntegerField(blank=True, null=True)
    slusatelji = models.ManyToManyField('urnik.Oseba', blank=True)
    letniki = models.ManyToManyField('urnik.Letnik', blank=True)

    class Meta:
        verbose_name_plural = 'predmeti'
        default_related_name = 'predmeti'
        ordering = ('ime',)

    def __str__(self):
        return self.ime

    def kratice_letnikov(self):
        return ', '.join(letnik.kratica for letnik in self.letniki.all())


class Semester(models.Model):
    ime = models.CharField(max_length=192)
    od = models.DateField()
    do = models.DateField()
    objavljen = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'semestri'
        ordering = ('od',)

    def __str__(self):
        return self.ime


class SrecanjeQuerySet(models.QuerySet):

    def odlozena(self):
        return self.filter(dan__isnull=True, ura__isnull=True).select_related('ucilnica', 'predmet').prefetch_related('ucitelji')

    def neodlozena(self):
        return self.filter(dan__isnull=False, ura__isnull=False)

    def prekrivanja(self):
        prekrivanja_ucilnic = defaultdict(set)
        prekrivanja_oseb = defaultdict(set)
        srecanja = self.neodlozena().select_related(
            'ucilnica',
        ).prefetch_related(
            'ucitelji',
            'predmet__slusatelji'
        )
        for srecanje in srecanja:
            for ura in range(srecanje.ura, srecanje.ura + srecanje.trajanje):
                for ucitelj in srecanje.ucitelji.all():
                    prekrivanja_oseb[(ucitelj, srecanje.dan, ura)].add(srecanje)
                if srecanje.predmet:
                    for slusatelj in srecanje.predmet.slusatelji.all():
                        prekrivanja_oseb[(slusatelj, srecanje.dan, ura)].add(srecanje)
                prekrivanja_ucilnic[(srecanje.ucilnica, srecanje.dan, ura)].add(srecanje)
        prekrivanja_po_tipih = {
            'Prekrivanja učilnic': prekrivanja_ucilnic,
            'Prekrivanja oseb': prekrivanja_oseb,
        }
        return {
            opis_tipa: {
                prekrivanje: srecanja
                for prekrivanje, srecanja in prekrivanja_tipa.items()
                if len(srecanja) > 1 and str(prekrivanje[0]).strip() != 'X'
            }
            for opis_tipa, prekrivanja_tipa in prekrivanja_po_tipih.items()
        }

    def urnik(self, skrij_rezervacije=False, barve=[]):
        if skrij_rezervacije:
            self = self.exclude(predmet__kratica='REZ')
        self = self.neodlozena(
        ).order_by(
            'dan', 'ura', 'trajanje'
        ).distinct(
        ).select_related(
            'ucilnica', 'predmet'
        ).prefetch_related(
            'predmet__letniki', 'ucitelji', 'predmet__slusatelji'
        )
        nastavi_sirine_srecanj(self)
        nastavi_barve(self, barve)
        return self

    def fiziki(self):
        FIZIKALNE_UCILNICE = (
            'F1', 'F2', 'F3', 'F4', 'F5', 'F7',
            'P.01', 'P.03', 'P.04',
            'MFP', 'VFP'
        )
        FIZIKALNE_SMERI = ('Fiz',)
        fizikalne_ucilnice = self.filter(ucilnica__oznaka__in=FIZIKALNE_UCILNICE)
        fizikalni_letniki = self.filter(predmet__letniki__smer__in=FIZIKALNE_SMERI)
        return (fizikalne_ucilnice | fizikalni_letniki).distinct()


class Termin(object):
    def __init__(self, dan, ura):
        self.dan = dan
        self.ura = ura

    def style(self):
        left = (self.dan - 1) * ENOTA_SIRINE
        top = (self.ura - MIN_URA) * ENOTA_VISINE
        height = ENOTA_VISINE
        width = ENOTA_SIRINE
        return 'position: absolute; left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%};'.format(left, width, top, height)


class TerminUrejanje(Termin):
    ZASEDEN = 'zaseden'

    def __init__(self, dan, ura, ustrezne, alternative, zasedenost_ucilnic, srecanje):
        super().__init__(dan, ura)
        self.ucilnice = []
        self.zasedenost = self.ZASEDEN
        ure = range(self.ura, self.ura + srecanje.trajanje)
        proste_ustrezne = False
        deloma_proste_ustrezne = False
        proste_alternative = False
        deloma_alternative = False

        for ucilnica in alternative:
            ucilnica = deepcopy(ucilnica)
            ucilnica.ustreznost = 'alternativa'
            self.ucilnice.append(ucilnica)
        for ucilnica in ustrezne:
            ucilnica = deepcopy(ucilnica)
            ucilnica.ustreznost = 'ustrezna'
            self.ucilnice.append(ucilnica)
        self.ucilnice.sort(key=lambda ucilnica:ucilnica.oznaka)

        def prosta(zasedenost_ucilnic, ucilnica, dan, ura):
            return ucilnica not in zasedenost_ucilnic.get((dan, ura), [])

        for ucilnica in self.ucilnice:
            if all(prosta(zasedenost_ucilnic, ucilnica, dan, ura) for ura in ure):
                ucilnica.zasedenost = 'prosta'
                if ucilnica.ustreznost == 'ustrezna':
                    proste_ustrezne = True
                else:
                    proste_alternative = True
            elif any(prosta(zasedenost_ucilnic, ucilnica, dan, ura) for ura in ure):
                ucilnica.zasedenost = 'deloma_prosta'
                if ucilnica.ustreznost == 'ustrezna':
                    deloma_proste_ustrezne = True
                else:
                    deloma_alternative = True
            else:
                ucilnica.zasedenost = 'zasedena'

        if proste_ustrezne:
            self.zasedenost = 'prosto'
        elif deloma_proste_ustrezne and proste_alternative:
            self.zasedenost = 'proste_le_alternative'
        elif deloma_proste_ustrezne:
            self.zasedenost = 'deloma'
        elif proste_alternative:
            self.zasedenost = 'proste_alternative'
        elif deloma_alternative:
            self.zasedenost = 'deloma_proste_alternative'


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
    def __init__(self, ustrezne_ucilnice, tip, velikost):
        self.ustrezne = ustrezne_ucilnice.filter(tip__in=tip).ustrezne_velikosti(velikost)
        self.zasedenost_ucilnic = defaultdict(dict)
        self.rezerviranost_ucilnic = defaultdict(dict)

    def dodaj_srecanja_semestra(self, semester):
        for srecanje in semester.srecanja.select_related('ucilnica', 'predmet').prefetch_related('ucitelji'
                                       ).filter(ucilnica__in=self.ustrezne).exclude(ura__isnull=True):
            for i in range(srecanje.trajanje):
                self.zasedenost_ucilnic[srecanje.dan, srecanje.ura + i][srecanje.ucilnica] = srecanje

    def upostevaj_rezervacije(self, teden):
        for rezervacija in Rezervacija.objects.filter(
            dan__gte=teden,
            dan__lte=teden+datetime.timedelta(days=6)
        ).prefetch_related(
            Prefetch(
                'ucilnice',
                queryset=Ucilnica.objects.filter(pk__in=self.ustrezne)
            ),
            'osebe'
        ):
            for ucilnica in rezervacija.ucilnice.all():
                for i in range(rezervacija.od, rezervacija.do):
                    self.rezerviranost_ucilnic[rezervacija.dan.isoweekday(), i][ucilnica] = rezervacija

    def dobi_termine(self):
        termini = [ProsteUcilniceTermin(d, u, self.ustrezne, self.zasedenost_ucilnic[d, u],
                                        self.rezerviranost_ucilnic[d, u])
                   for d in range(1, len(DNEVI) + 1) for u in range(MIN_URA, MAX_URA)]
        return termini


class Srecanje(models.Model):
    PREDAVANJA, SEMINAR, VAJE, LABORATORIJSKE_VAJE = 'P', 'S', 'V', 'L'
    TIP = (
        (PREDAVANJA, 'predavanja'), (SEMINAR, 'seminar'),
        (VAJE, 'vaje'), (LABORATORIJSKE_VAJE, 'laboratorijske vaje'),
    )
    semester = models.ForeignKey('urnik.Semester')
    predmet = models.ForeignKey('urnik.Predmet', null=True, blank=True, on_delete=models.CASCADE)
    tip = models.CharField(max_length=1, choices=TIP, blank=True)
    oznaka = models.CharField(max_length=64, blank=True)
    ucitelji = models.ManyToManyField('urnik.Oseba', blank=True)
    dan = models.PositiveSmallIntegerField(choices=enumerate(DNEVI, 1), blank=True, null=True)
    ura = models.PositiveSmallIntegerField(blank=True, null=True)
    trajanje = models.PositiveSmallIntegerField(null=True)
    ucilnica = models.ForeignKey('urnik.Ucilnica', null=True, blank=True, on_delete=models.SET_NULL)
    objects = SrecanjeQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'srečanja'
        default_related_name = 'srecanja'
        ordering = ('predmet', 'tip', 'oznaka', 'dan', 'ura', 'trajanje')

    def __str__(self):
        if self.dan and self.ura:
            return '{}, {}{}, {}, {}, {}–{}, {}'.format(
                self.predmet, self.tip, self.oznaka, ', '.join(str(ucitelj) for ucitelj in self.ucitelji.all()),
                self.get_dan_display(), self.ura, self.ura + self.trajanje,
                self.ucilnica
            )
        else:
            return '{}, {}{}, {}, odloženo, {}'.format(
                self.predmet, self.tip, self.oznaka, ', '.join(str(ucitelj) for ucitelj in self.ucitelji.all()),
                self.ucilnica
            )

    @property
    def od(self):
        return self.ura

    @property
    def do(self):
        if self.ura:
            return self.ura + self.trajanje

    def podvoji(self):
        stari_ucitelji = list(self.ucitelji.all())
        self.id = None
        self.save()
        for ucitelj in stari_ucitelji:
            self.ucitelji.add(ucitelj)

    def odlozi(self):
        self.dan = None
        self.ura = None
        self.save()

    def nastavi_trajanje(self, trajanje):
        self.trajanje = trajanje
        self.save()

    def premakni(self, dan, ura, ucilnica):
        self.dan = dan
        self.ura = ura
        self.ucilnica = ucilnica
        self.save()

    def lahko_skrajsam(self):
        return self.trajanje > 1

    def lahko_podaljsam(self):
        return not self.ura or self.ura + self.trajanje < MAX_URA

    def lahko_odlozim(self):
        return self.dan and self.ura

    def po_potrebi_okrajsano_ime_predmeta(self):
        if hasattr(self, 'sirina') and ((self.sirina >= 0.5 and len(self.predmet.ime) < 45 and self.trajanje > 1) or self.sirina == 1):
            return self.predmet.ime
        else:
            return self.predmet.kratica

    def povezana_srecanja(self):
        srecanja = self.semester.srecanja
        letniki_poslusajo = srecanja.filter(predmet__letniki__in=self.predmet.letniki.all())
        ucitelj_uci = srecanja.filter(ucitelji__in=self.ucitelji.all())
        ucitelj_poslusa = srecanja.filter(predmet__slusatelji__in=self.ucitelji.all())
        return (letniki_poslusajo | ucitelj_uci | ucitelj_poslusa).exclude(
            pk=self.pk
        ).distinct()

    def style(self):
        if self.dan and self.ura and hasattr(self, 'sirina'):
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
        if hasattr(self, 'leftmost') and self.leftmost: classes.append('leftmost')
        if hasattr(self, 'rightmost') and self.rightmost: classes.append('rightmost')
        return ' '.join(classes)

    def prosti_termini(self, tip, oddelek):
        ustrezne, alternative = Ucilnica.objects.ustrezne(tip=tip, oddelek=oddelek)
        if self.ucilnica not in ustrezne and self.ucilnica not in alternative:
            ustrezne.insert(0, self.ucilnica)

        zasedenost_ucilnic = defaultdict(set)
        for srecanje in self.semester.srecanja.neodlozena().filter(ucilnica__in=ustrezne + alternative).exclude(pk=self.pk).select_related('ucilnica'):
            for ura in range(srecanje.ura, srecanje.ura + srecanje.trajanje):
                zasedenost_ucilnic[(srecanje.dan, ura)].add(srecanje.ucilnica)

        termini = {}
        for dan in range(1, 6):
            for ura in range(MIN_URA, MAX_URA - self.trajanje + 1):
                termini[(dan, ura)] = TerminUrejanje(
                    dan=dan,
                    ura=ura,
                    ustrezne=ustrezne,
                    alternative=alternative,
                    zasedenost_ucilnic=zasedenost_ucilnic,
                    srecanje=self,
                )
        return termini


class RezervacijaQuerySet(models.QuerySet):

    def prihajajoce(self):
        return self.filter(dan__gte=datetime.date.today())


class Rezervacija(models.Model):
    ucilnice = models.ManyToManyField('urnik.Ucilnica')
    osebe = models.ManyToManyField('urnik.Oseba')
    dan = models.DateField()
    od = models.PositiveSmallIntegerField()
    do = models.PositiveSmallIntegerField()
    opomba = models.CharField(max_length=192)
    objects = RezervacijaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'rezervacije'
        default_related_name = 'rezervacije'
        ordering = ('dan', 'od', 'do')

    # def clean(self):
    #     if not self.osebe.exists() and not self.opomba:
    #         raise ValidationError('Rezervaciji dodajte vsaj eno osebo ali vpišite opombo.')
    #     return self

    def teden(self):
        start = self.dan - datetime.timedelta(days=self.dan.weekday())
        end = start + datetime.timedelta(days=6)
        return (start, end)

    def konflikti(self):
        for ucilnica in self.ucilnice.all():
            for srecanje in ucilnica.srecanja.all():
                if self.dan.weekday() + 1 != srecanje.dan or not srecanje.od:
                    continue
                elif srecanje.do <= self.od:
                    continue
                elif self.do <= srecanje.od:
                    continue
                else:
                    yield srecanje
