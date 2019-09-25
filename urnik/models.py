import datetime
import icu
from collections import defaultdict
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm, CheckboxSelectMultiple, TextInput, DateInput, BooleanField, ModelMultipleChoiceField
from django.template import defaultfilters

from urnik.templatetags.tags import dan_tozilnik_mnozina
from urnik.utils import teden_dneva
from .layout import nastavi_sirine_srecanj, nastavi_barve

MIN_URA, MAX_URA = 7, 20
ENOTA_VISINE = 1 / (MAX_URA - MIN_URA)
DNEVI = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
ENOTA_SIRINE = 1 / len(DNEVI)
DAYS_IN_WEEK = 7

collator = icu.Collator.createInstance(icu.Locale(settings.LANGUAGE_CODE))


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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='oseba')

    objects = OsebaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'osebe'
        default_related_name = 'osebe'
        ordering = ('priimek', 'ime')

    @property
    def priimek_ime(self):
        if self.ime:
            return '{} {}'.format(self.priimek, self.ime)
        else:
            return self.priimek

    def __str__(self):
        if self.ime:
            return '{} {}'.format(self.ime, self.priimek)
        else:
            return self.priimek

    def __lt__(self, other):
        return self.vrstni_red() < other.vrstni_red()

    def vrstni_red(self):
        if self.ime:
            return (collator.getSortKey(self.priimek), collator.getSortKey(self.ime))
        else:
            return (collator.getSortKey(self.priimek), )

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
        return self.vrstni_red() < other.vrstni_red()

    def kratko_ime(self):
        if self.kratka_oznaka:
            return self.kratka_oznaka
        return self.oznaka

    def vrstni_red(self):
        return collator.getSortKey(self.oznaka)


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


class SemesterQuerySet(models.QuerySet):
    def v_obdobju(self, od, do):
        return self.filter(do__gte=od, od__lte=do)


class Semester(models.Model):
    ime = models.CharField(max_length=192)
    od = models.DateField()
    do = models.DateField()
    objavljen = models.BooleanField(default=False)

    objects = SemesterQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'semestri'
        ordering = ('od',)

    def __str__(self):
        return self.ime
    
    def pripravi_kopijo(self):
        novi_semester = Semester.objects.create(
            ime=self.ime + ' (kopija)',
            od=self.od + datetime.timedelta(days=365),
            do=self.do + datetime.timedelta(days=365),
            objavljen=False
        )
        for srecanje in self.srecanja.all():
            srecanje.podvoji(novi_semester=novi_semester)
        return novi_semester

    def prihodnji_tedni(self):
        razlika = datetime.timedelta(weeks=1)
        tedni = set()
        danes = datetime.date.today()
        dan = danes
        while dan < self.do:
            tedni.add(teden_dneva(dan))
            dan += razlika
        if self.do >= danes:
            tedni.add(teden_dneva(self.do))
        return tedni


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

    def urnik(self, barve=[]):
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
        self.ucilnice.sort()

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


class Srecanje(models.Model):
    PREDAVANJA, SEMINAR, VAJE, LABORATORIJSKE_VAJE = 'P', 'S', 'V', 'L'
    TIP = (
        (PREDAVANJA, 'predavanja'), (SEMINAR, 'seminar'),
        (VAJE, 'vaje'), (LABORATORIJSKE_VAJE, 'laboratorijske vaje'),
    )
    semester = models.ForeignKey('urnik.Semester', on_delete=models.PROTECT)
    predmet = models.ForeignKey('urnik.Predmet', null=True, blank=True, on_delete=models.SET_NULL)
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

    def se_po_urah_prekriva(self, od, do):
        return self.od < do and od < self.do

    def podvoji(self, novi_semester=None):
        stari_ucitelji = list(self.ucitelji.all())
        self.id = None
        if novi_semester is not None:
            self.semester = novi_semester
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
        return not self.ura or self.do < MAX_URA

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

    def dnevi_med(self, od, do):
        od = max(od, self.semester.od)
        dan = od + datetime.timedelta((self.dan - (od.weekday()+1)) % DAYS_IN_WEEK)
        assert dan.weekday() + 1 == self.dan, "Ups."
        dan_konca = min(self.semester.do, do)
        razlika = datetime.timedelta(weeks=1)
        while dan <= dan_konca:
            yield dan
            dan += razlika


class RezervacijaQuerySet(models.QuerySet):

    def v_tednu(self, ponedeljek):
        nedelja = ponedeljek + datetime.timedelta(days=6)
        return self.filter(
            dan_konca__isnull=True,
            dan__gte=ponedeljek,
            dan__lte=nedelja,
        ) | self.filter(
            dan_konca__isnull=False,
            dan__lte=nedelja,
        ).exclude(
            dan_konca__lt=ponedeljek,
        )

    def prihajajoce(self):
        return self.filter(dan__gte=datetime.date.today()) | self.filter(dan_konca__gte=datetime.date.today())


class Rezervacija(models.Model):
    ucilnice = models.ManyToManyField('urnik.Ucilnica', blank=False,
                                      limit_choices_to={'tip__in': Ucilnica.OBJAVLJENI_TIPI}, verbose_name='Učilnice')
    osebe = models.ManyToManyField('urnik.Oseba', verbose_name='Osebe')
    dan = models.DateField(verbose_name='Dan začetka', blank=False, null=False, help_text='Za kateri dan želite rezervirati')
    dan_konca = models.DateField(blank=True, null=True, verbose_name='Dan konca', help_text='Dan konca rezervacije; izpolnite le, če je drugačen od začetka')
    MOZNE_URE = tuple((u, str(u)+":00") for u in range(MIN_URA, MAX_URA+1))
    od = models.PositiveSmallIntegerField(blank=False, null=False, choices=MOZNE_URE, help_text='Od katere ure želite rezervirati')
    do = models.PositiveSmallIntegerField(blank=False, null=False, choices=MOZNE_URE, help_text='Do katere ure želite rezervirati')
    opomba = models.CharField(max_length=192, blank=False, null=False, help_text='Razlog za rezervacijo')
    potrjena = models.BooleanField(default=False, null=False, help_text='Ali so to rezervacijo potrdili posvečeni ljudje')
    avtor_rezervacije = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, help_text='Kdo je dejansko naredil rezervacijo', on_delete=models.CASCADE)
    cas_rezervacije = models.DateTimeField(auto_now_add=True, help_text="Datum in čas, ko je bila rezervacija narejena", verbose_name='Datum in čas rezervacije')

    objects = RezervacijaQuerySet.as_manager()

    @property
    def zacetek(self):
        return self.dan

    @property
    def konec(self):
        return self.dan_konca or self.dan

    def __str__(self):
        if self.dan_konca:
            return "Rezervacija od {} do {}, {}–{} za {}".format(self.zacetek, self.konec, self.od, self.do, self.opomba)
        else:
            return "Rezervacija dne {}, {}–{} za {}".format(self.zacetek, self.od, self.do, self.opomba)

    class Meta:
        verbose_name_plural = 'rezervacije'
        default_related_name = 'rezervacije'
        ordering = ('dan', 'od', 'do')

    def dnevi(self):
        return self.dnevi_med(self.zacetek, self.konec)

    def prihajajoci_dnevi(self):
        return self.dnevi_med(datetime.date.today(), self.konec)

    def dnevi_med(self, od, do):
        dan = max(self.zacetek, od)
        dan_konca = min(self.konec, do)
        razlika = datetime.timedelta(days=1)
        while dan <= dan_konca:
            yield dan
            dan += razlika

    def se_po_urah_prekriva(self, od, do):
        return self.od < do and od < self.do


class RezervacijeModelMultipleChoiceField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        ModelMultipleChoiceField.__init__(self, *args, **kwargs)
        it = self.iterator(self)
        self.choices = [it.choice(obj) for obj in sorted(self.queryset)]


class OsebeModelMultipleChoiceField(RezervacijeModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.priimek_ime


class UcilniceModelMultipleChoiceField(RezervacijeModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.oznaka


class RezevacijeForm(ModelForm):

    PREKRIVANJA = 'prekrivanja'

    osebe = OsebeModelMultipleChoiceField(queryset=Oseba.objects.all(),
                                          help_text='Osebe, ki si lastijo to rezervacijo')
    ucilnice = UcilniceModelMultipleChoiceField(queryset=Ucilnica.objects.objavljene(),
                                                help_text='Izberite učilnice, ki jih želite rezervirati',
                                                widget=CheckboxSelectMultiple())
    use_required_attribute = False

    class Meta:
        model = Rezervacija
        fields = ['ucilnice', 'osebe', 'dan', 'dan_konca', 'od', 'do', 'opomba']
        widgets = {
            'dan': DateInput(attrs={'placeholder': 'npr. 15. 1. 2019', 'class': 'datepicker'}),
            'dan_konca': DateInput(attrs={'placeholder': 'ponavadi prazno, lahko tudi npr. 17. 1. 2019', 'class': 'datepicker'}),
            'opomba': TextInput(attrs={'placeholder': 'npr. izpit Analiza 1 FIN'}),
        }

    def __init__(self, *args, **kwargs):
        dovoli_prekrivanja = kwargs.pop('dovoli_prekrivanja', None)
        super(RezevacijeForm, self).__init__(*args, **kwargs)
        if dovoli_prekrivanja:
            self.fields['ignoriraj_prekrivanja'] = BooleanField(
                required=False, initial=False,
                help_text='Zavedam se prekrivanj in vseeno želim rezervirati izbrane učilnice '
                          'v izbranih dnevih in urah.')

    def clean_dan(self):
        dan = self.cleaned_data['dan']
        if dan < datetime.date.today():
            raise ValidationError("Datum rezervacije mora biti v prihodnosti.")
        return dan

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned

        od = cleaned.get('od')
        do = cleaned.get('do')
        if od >= do:
            self.add_error(None, ValidationError("Ura začetka rezervacije mora biti pred uro konca rezervacije."))

        dan = cleaned.get('dan')
        konec = cleaned.get('dan_konca')
        if konec:
            if dan == konec:
                self.cleaned_data['dan_konca'] = None
            elif dan > konec:
                self.add_error(None, ValidationError("Dan začetka rezervacije moda biti "
                                                     "pred dnevom konca rezervacije."))
        ignoriraj = cleaned.get('ignoriraj_prekrivanja')
        if not ignoriraj:
            self._preveri_konflikte(cleaned)

        return self.cleaned_data

    def _preveri_konflikte(self, cleaned):
        from urnik.iskanik_konfliktov import IskalnikKonfliktov
        ucilnice = cleaned.get('ucilnice')
        dan = cleaned.get('dan')
        konec = cleaned.get('dan_konca') or dan
        od = cleaned.get('od')
        do = cleaned.get('do')
        iskalnik = IskalnikKonfliktov(ucilnice, dan, konec)
        iskalnik.dodaj_srecanja()
        iskalnik.dodaj_rezervacije(Rezervacija.objects.prihajajoce())

        date_format = lambda d: defaultfilters.date(d, "D, j. b")
        for u in ucilnice:
            d = dan
            while d <= konec:
                konflikti = iskalnik.konflikti(u, d, od, do)
                for r in konflikti.rezervacije:
                    oseba = r.osebe.all()[:1]
                    self.add_error(None, ValidationError(
                        'Vaša rezervacija bi se prekrivala z rezervacijo osebe %(oseba)s %(dan)s '
                        'od %(od)i do %(do)i z razlogom %(razlog)s.',
                        params={
                            'oseba': oseba[0] if oseba else 'neznan',
                            'dan': "od {} do {}".format(date_format(r.dan), date_format(r.dan_konca))
                            if r.dan_konca else "dne {}".format(date_format(r.dan)),
                            'razlog': r.opomba,
                            'od': r.od,
                            'do': r.do,
                        },
                        code=RezevacijeForm.PREKRIVANJA,
                    ))

                for s in konflikti.srecanja:
                    self.add_error(None, ValidationError(
                        'Vaša rezervacija bi se prekrivala s predmetom %(predmet)s (%(semester)s), ki se izvaja '
                        'ob %(dan_v_tednu)s od %(od)i do %(do)i.',
                        params={
                            'predmet': s.predmet,
                            'semester': s.semester,
                            'dan_v_tednu': dan_tozilnik_mnozina(s.dan),
                            'od': s.od,
                            'do': s.do,
                        },
                        code=RezevacijeForm.PREKRIVANJA,
                    ))

                d += datetime.timedelta(days=1)
