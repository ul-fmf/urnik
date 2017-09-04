from collections import defaultdict
from copy import deepcopy
from django.db import models
from .layout import nastavi_sirine_srecanj

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
        return '{} {}'.format(self.ime, self.priimek)


class Letnik(models.Model):
    smer = models.CharField(max_length=192)
    leto = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'letniki'
        default_related_name = 'letniki'
        ordering = ('smer', 'leto')

    def __str__(self):
        if self.leto:
            return '{}, {}. letnik'.format(self.smer, self.leto)
        else:
            return self.smer

    def srecanja(self):
        return Srecanje.objects.filter(predmet__letniki=self).distinct()


class UcilnicaQuerySet(models.QuerySet):

    def ustrezne(self, stevilo_studentov=None, racunalniska=False):
        ucilnice = self.filter(velikost__isnull=False, racunalniska__gte=racunalniska)
        if stevilo_studentov:
            ucilnice = list(ucilnice.filter(velikost__gt=2 / 3 * stevilo_studentov))
        else:
            ucilnice = list(ucilnice)
        for ucilnica in ucilnice:
            if not stevilo_studentov or ucilnica.velikost / stevilo_studentov <= 3/4:
                ucilnica.ustreznost = 'morebiti'
            else:
                ucilnica.ustreznost = 'ustrezna'
        return ucilnice


class Ucilnica(models.Model):
    oznaka = models.CharField(max_length=192, unique=True)
    velikost = models.PositiveSmallIntegerField(blank=True, null=True)
    racunalniska = models.BooleanField(default=False)
    vidna = models.BooleanField(default=True)
    objects = UcilnicaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'ucilnice'
        default_related_name = 'ucilnice'
        ordering = ('oznaka',)

    def __str__(self):
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


class SrecanjeQuerySet(models.QuerySet):

    def odlozena(self):
        return self.filter(dan__isnull=True, ura__isnull=True).select_related('ucilnica', 'ucitelj', 'predmet')

    def neodlozena(self):
        return self.filter(dan__isnull=False, ura__isnull=False)

    def prekrivanja(self):
        prekrivanja_ucilnic = defaultdict(set)
        prekrivanja_oseb = defaultdict(set)
        prekrivanja_letnikov = defaultdict(set)
        srecanja = self.neodlozena().select_related(
            'ucilnica',
            'ucitelj'
        ).prefetch_related(
            'predmet__letniki',
            'predmet__slusatelji'
        )
        for srecanje in srecanja:
            for ura in range(srecanje.ura, srecanje.ura + srecanje.trajanje):
                prekrivanja_oseb[(srecanje.ucitelj, srecanje.dan, ura)].add(srecanje)
                for slusatelj in srecanje.predmet.slusatelji.all():
                    prekrivanja_oseb[(slusatelj, srecanje.dan, ura)].add(srecanje)
                prekrivanja_ucilnic[(srecanje.ucilnica, srecanje.dan, ura)].add(srecanje)
                for letnik in srecanje.predmet.letniki.all():
                    prekrivanja_letnikov[(letnik, srecanje.dan, ura)].add(srecanje)
        prekrivanja_po_tipih = {
            'Prekrivanja učilnic': prekrivanja_ucilnic,
            'Prekrivanja oseb': prekrivanja_oseb,
            'Prekrivanja letnikov': prekrivanja_letnikov,
        }
        return {
            opis_tipa: {
                prekrivanje: srecanja
                for prekrivanje, srecanja in prekrivanja_tipa.items()
                if len(srecanja) > 1
            }
            for opis_tipa, prekrivanja_tipa in prekrivanja_po_tipih.items()
        }

    def urnik(self, skrij_rezervacije=False):
        if skrij_rezervacije:
            self = self.exclude(predmet__kratica='REZ')
        self = self.neodlozena(
        ).order_by(
            'dan', 'ura', 'trajanje'
        ).distinct(
        ).select_related(
            'ucilnica', 'ucitelj', 'predmet'
        )
        nastavi_sirine_srecanj(self)
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


class Termin:
    ZASEDEN = 'zaseden'

    def __init__(self, dan, ura, ucilnice, zasedenost_ucilnic, srecanje):
        self.dan = dan
        self.ura = ura
        self.ucilnice = deepcopy(ucilnice)
        self.zasedenost = self.ZASEDEN
        ure = range(self.ura, self.ura + srecanje.trajanje)
        proste_prave = False
        deloma_prave = False
        proste_alternative = False
        deloma_alternative = False

        def prosta(zasedenost_ucilnic, ucilnica, dan, ura):
            return ucilnica not in zasedenost_ucilnic.get((dan, ura), [])

        for ucilnica in self.ucilnice:
            if all(prosta(zasedenost_ucilnic, ucilnica, dan, ura) for ura in ure):
                ucilnica.zasedenost = 'prosta'
                if ucilnica.ustreznost == 'ustrezna':
                    proste_prave = True
                else:
                    proste_alternative = True
            elif any(prosta(zasedenost_ucilnic, ucilnica, dan, ura) for ura in ure):
                ucilnica.zasedenost = 'deloma_prosta'
                if ucilnica.ustreznost == 'ustrezna':
                    deloma_prave = True
                else:
                    deloma_alternative = True
            else:
                ucilnica.zasedenost = 'zasedena'

        if proste_prave:
            self.zasedenost = 'prosto'
        elif deloma_prave and proste_alternative:
            self.zasedenost = 'proste_le_alternative'
        elif deloma_prave and deloma_alternative:
            self.zasedenost = 'vse_mogoce'
        elif deloma_prave:
            self.zasedenost = 'deloma'
        elif proste_alternative:
            self.zasedenost = 'proste_alternative'
        elif deloma_alternative:
            self.zasedenost = 'deloma_proste_alternative'

    def style(self):
        left = (self.dan - 1) * ENOTA_SIRINE
        top = (self.ura - MIN_URA) * ENOTA_VISINE
        height = ENOTA_VISINE
        width = ENOTA_SIRINE
        return 'position: absolute; left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)


class Srecanje(models.Model):
    PREDAVANJA, SEMINAR, VAJE, LABORATORIJSKE_VAJE = 'P', 'S', 'V', 'L'
    TIP = (
        (PREDAVANJA, 'predavanja'), (SEMINAR, 'seminar'),
        (VAJE, 'vaje'), (LABORATORIJSKE_VAJE, 'laboratorijske vaje'),
    )
    predmet = models.ForeignKey('urnik.Predmet', null=True, blank=True, on_delete=models.CASCADE)
    tip = models.CharField(max_length=1, choices=TIP, blank=True)
    oznaka = models.CharField(max_length=64, blank=True)
    ucitelj = models.ForeignKey('urnik.Oseba', null=True, blank=True, on_delete=models.SET_NULL)
    dan = models.PositiveSmallIntegerField(choices=enumerate(DNEVI), blank=True, null=True)
    ura = models.PositiveSmallIntegerField(blank=True, null=True)
    trajanje = models.PositiveSmallIntegerField(null=True)
    ucilnica = models.ForeignKey('urnik.Ucilnica', null=True, blank=True, on_delete=models.SET_NULL)
    objects = SrecanjeQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'srečanja'
        default_related_name = 'srecanja'
        ordering = ('predmet', 'tip', 'oznaka', 'ucitelj', 'dan', 'ura', 'trajanje')

    def __str__(self):
        if self.dan and self.ura:
            return '{}, {}{}, {}, {}, {}–{}, {}'.format(
                self.predmet, self.tip, self.oznaka, self.ucitelj,
                self.get_dan_display(), self.ura, self.ura + self.trajanje,
                self.ucilnica
            )
        else:
            return '{}, {}{}, {}, odloženo, {}'.format(
                self.predmet, self.tip, self.oznaka, self.ucitelj,
                self.ucilnica
            )

    def podvoji(self):
        self.id = None
        self.save()

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
        if 'sirina' in vars(self) and ((self.sirina >= 0.5 and len(self.predmet.ime) < 45 and self.trajanje > 1) or self.sirina == 1):
            return self.predmet.ime
        else:
            return self.predmet.kratica

    def povezana_srecanja(self):
        letniki_poslusajo = Srecanje.objects.filter(predmet__letniki__in=self.predmet.letniki.all())
        ucitelj_uci = Srecanje.objects.filter(ucitelj=self.ucitelj)
        ucitelj_poslusa = Srecanje.objects.filter(predmet__slusatelji=self.ucitelj)
        return (letniki_poslusajo | ucitelj_uci | ucitelj_poslusa).exclude(
            pk=self.pk
        ).distinct()

    def style(self):
        if self.dan and self.ura and 'sirina' in vars(self):
            left = (self.dan - 1 + self.zamik) * ENOTA_SIRINE
            top = (self.ura - MIN_URA) * ENOTA_VISINE
            height = self.trajanje * ENOTA_VISINE
            width = self.sirina * ENOTA_SIRINE
            return 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(
                left, width, top, height
            )
        else:
            return ''

    def prosti_termini(self):
        ucilnice = Ucilnica.objects.ustrezne(stevilo_studentov=self.predmet.stevilo_studentov)
        if self.ucilnica not in ucilnice:
            self.ucilnica.ustreznost = 'ustrezna'
            ucilnice.insert(0, self.ucilnica)

        zasedenost_ucilnic = defaultdict(set)
        for srecanje in Srecanje.objects.neodlozena().filter(ucilnica__in=ucilnice).exclude(pk=self.pk).select_related('ucilnica'):
            for ura in range(srecanje.ura, srecanje.ura + srecanje.trajanje):
                zasedenost_ucilnic[(srecanje.dan, ura)].add(srecanje.ucilnica)

        termini = {}
        for dan in range(1, 6):
            for ura in range(MIN_URA, MAX_URA - self.trajanje + 1):
                termini[(dan, ura)] = Termin(
                    dan=dan,
                    ura=ura,
                    ucilnice=ucilnice,
                    zasedenost_ucilnic=zasedenost_ucilnic,
                    srecanje=self,
                )
        return termini
