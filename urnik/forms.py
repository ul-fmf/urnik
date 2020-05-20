import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField, forms, CheckboxSelectMultiple, DateInput, TextInput, \
    BooleanField
from django.template import defaultfilters

from urnik.models import Oseba, Predmet, Ucilnica, Rezervacija
from urnik.templatetags.tags import dan_tozilnik_mnozina


class PredmetModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.opisno_ime()


class OsebeModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.priimek_ime


class UcilniceModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.oznaka


class KombiniranPogledForm(forms.Form):
    oseba = OsebeModelMultipleChoiceField(queryset=Oseba.objects.aktivni(), required=False)
    predmet = PredmetModelMultipleChoiceField(queryset=Predmet.objects.exclude(ime="").prefetch_related('letniki'), required=False)


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
