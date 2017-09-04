from copy import deepcopy
from django.db import models
from .layout import nastavi_sirine_srecanj

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
        ucilnice = {}
        osebe = {}
        smeri = {}
        for srecanje in self.neodlozena().select_related('ucilnica', 'ucitelj').prefetch_related('predmet__letniki', 'predmet__slusatelji'):
            for ura in range(srecanje.ura, srecanje.ura + srecanje.trajanje):
                osebe.setdefault((srecanje.ucitelj, srecanje.dan, ura), set()).add(srecanje)
                for slusatelj in srecanje.predmet.slusatelji.all():
                    osebe.setdefault((slusatelj, srecanje.dan, ura), set()).add(srecanje)
                ucilnice.setdefault((srecanje.ucilnica, srecanje.dan, ura), set()).add(srecanje)
                for letnik in srecanje.predmet.letniki.all():
                    smeri.setdefault((letnik, srecanje.dan, ura), set()).add(srecanje)
        prekrivanja_po_tipih = {
            'Konflikti učilnic': ucilnice,
            'Konflikti oseb': osebe,
            'Konflikti smeri': smeri,
        }
        return {
            opis: {konflikt: srecanja for konflikt, srecanja in prekrivanja.items() if len(srecanja) > 1}
            for opis, prekrivanja in prekrivanja_po_tipih.items()
        }

    def urnik(self, skrij_rezervacije=False):
        if skrij_rezervacije:
            self = self.exclude(predmet__kratica='REZ')
        return nastavi_sirine_srecanj(self.neodlozena().order_by('dan', 'ura', 'trajanje').distinct().select_related('ucilnica', 'ucitelj', 'predmet'))

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


class Srecanje(models.Model):
    PREDAVANJA, SEMINAR, VAJE, LABORATORIJSKE_VAJE = 'P', 'S', 'V', 'L'
    TIP = (
        (PREDAVANJA, 'predavanja'), (SEMINAR, 'seminar'),
        (VAJE, 'vaje'), (LABORATORIJSKE_VAJE, 'laboratorijske vaje'),
    )
    PONEDELJEK, TOREK, SREDA, CETRTEK, PETEK = 1, 2, 3, 4, 5
    DAN = (
        (PONEDELJEK, 'ponedeljek'), (TOREK, 'torek'), (SREDA, 'sreda'),
        (CETRTEK, 'četrtek'), (PETEK, 'petek'),
    )
    predmet = models.ForeignKey('urnik.Predmet', null=True, blank=True, on_delete=models.CASCADE)
    tip = models.CharField(max_length=1, choices=TIP, blank=True)
    oznaka = models.CharField(max_length=64, blank=True)
    ucitelj = models.ForeignKey('urnik.Oseba', null=True, blank=True, on_delete=models.SET_NULL)
    dan = models.PositiveSmallIntegerField(choices=DAN, blank=True, null=True)
    ura = models.PositiveSmallIntegerField(blank=True, null=True)
    trajanje = models.PositiveSmallIntegerField(null=True)
    ucilnica = models.ForeignKey('urnik.Ucilnica', null=True, blank=True, on_delete=models.SET_NULL)
    objects = SrecanjeQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'srecanja'
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

    def povezana_srecanja(self):
        letniki_poslusajo = Srecanje.objects.filter(predmet__letniki__in=self.predmet.letniki.all())
        ucitelj_uci = Srecanje.objects.filter(ucitelj=self.ucitelj)
        ucitelj_poslusa = Srecanje.objects.filter(predmet__slusatelji=self.ucitelj)
        return (letniki_poslusajo | ucitelj_uci | ucitelj_poslusa).exclude(
            pk=self.pk
        ).distinct()

    def style(self):
        min_ura, max_ura = 7, 20
        enota_visine = 1 / (max_ura - min_ura)
        dnevi = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
        enota_sirine = 1 / len(dnevi)
        left = (self.dan - 1 + self.zamik) * enota_sirine
        top = (self.ura - min_ura) * enota_visine
        height = self.trajanje * enota_visine
        width = self.sirina * enota_sirine
        return 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(
            left, width, top, height
        )

    def prosti_termini(self):
        def oznaci_zasedenost(izbrano_srecanje, ucilnice):
            zasedene = {}
            for zasedenost in Srecanje.objects.neodlozena().filter(ucilnica__in=ucilnice).exclude(pk=izbrano_srecanje.pk).select_related('ucilnica'):
                dan = zasedenost.dan
                for ura in range(zasedenost.ura, zasedenost.ura + zasedenost.trajanje):
                    zasedene.setdefault((dan, ura), set()).add(zasedenost.ucilnica)

            def prosta(ucilnica, dan, ura):
                return ucilnica not in zasedene.get((dan, ura), [])

            termini = {}
            for dan in range(1, 6):
                for zacetek in range(7, 20 - izbrano_srecanje.trajanje + 1):
                    termin = termini.setdefault((dan, zacetek), {
                        'ucilnice': deepcopy(ucilnice),
                        'zasedenost': 'zaseden'
                    })
                    ure = range(zacetek, zacetek + izbrano_srecanje.trajanje)
                    proste_prave = False
                    deloma_prave = False
                    proste_alternative = False
                    deloma_alternative = False
                    for ucilnica in termin['ucilnice']:
                        if all(prosta(ucilnica, dan, ura) for ura in ure):
                            ucilnica.zasedenost = 'prosta'
                            if ucilnica.ustreznost == 'ustrezna':
                                proste_prave = True
                            else:
                                proste_alternative = True
                        elif any(prosta(ucilnica, dan, ura) for ura in ure):
                            ucilnica.zasedenost = 'deloma_prosta'
                            if ucilnica.ustreznost == 'ustrezna':
                                deloma_prave = True
                            else:
                                deloma_alternative = True
                        else:
                            ucilnica.zasedenost = 'zasedena'
                    if proste_prave:
                        termin['zasedenost'] = 'prosto'
                    elif deloma_prave and proste_alternative:
                        termin['zasedenost'] = 'proste_le_alternative'
                    elif deloma_prave and deloma_alternative:
                        termin['zasedenost'] = 'vse_mogoce'
                    elif deloma_prave:
                        termin['zasedenost'] = 'deloma'
                    elif proste_alternative:
                        termin['zasedenost'] = 'proste_alternative'
                    elif deloma_alternative:
                        termin['zasedenost'] = 'deloma_proste_alternative'

            return termini
        ucilnice = Ucilnica.objects.ustrezne(stevilo_studentov=self.predmet.stevilo_studentov)
        for ucilnica in ucilnice:
            if ucilnica == self.ucilnica:
                break
        else:
            ucilnica = self.ucilnica
            ucilnica.ustreznost = 'ustrezna'
            ucilnice = [ucilnica] + ucilnice
        ucilnice = oznaci_zasedenost(self, ucilnice)
        return ucilnice