from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Rezervacija, Semester

class RezervacijaForm(forms.ModelForm):
    """
    Ta forma omogoca vecjo kontrolo nad vnosom rezervacij.
    Med drugim ponuja validacijo; v primeru, da se vnesena rezervacija prekriva
    z srecanjem ali rezervacijo, je raisan exception.
    """
    opomba = forms.CharField(label='Razlog rezervacije')

    class Meta:
        model = Rezervacija
        fields = ['ucilnice', 'osebe', 'dan', 'od', 'do', 'opomba']

    def clean(self):
        def konflikti_srecanja(ucilnice):
            semester_okoli_datuma = Semester.objects.filter(od__lte=self.cleaned_data['dan'], do__gte=self.cleaned_data['dan'])
            for ucilnica in ucilnice.all():
                for srecanje in ucilnica.srecanja.filter(semester__in=semester_okoli_datuma):
                    if self.cleaned_data['dan'].weekday() + 1 != srecanje.dan or not srecanje.od:
                        continue
                    elif srecanje.do <= self.cleaned_data['od']:
                        continue
                    elif self.cleaned_data['do'] <= srecanje.od:
                        continue
                    else:
                        yield srecanje

        def konflikti_rezervacije(ucilnice):
            for ucilnica in ucilnice.all():
                for rezervacija in ucilnica.rezervacije.filter(dan = self.cleaned_data['dan']).exclude(id=self.instance.id):
                    if rezervacija.do <= self.cleaned_data['od']:
                        continue
                    elif self.cleaned_data['do'] <= rezervacija.od:
                        continue
                    else:
                        yield rezervacija

        errors = []
        dan = self.cleaned_data['dan'].strftime('%d. %b %Y')
        if 'ucilnice' in self.cleaned_data:
            for srecanje in konflikti_srecanja(self.cleaned_data['ucilnice']):
                errors.append(forms.ValidationError(
                    'Vaša rezervacija se prekriva s predmetom %(predmet)s (%(semester)s), ki se izvaja %(dan)s od %(od)i do %(do)i.',
                    params = {
                        'predmet': srecanje.predmet,
                        'semester': srecanje.semester,
                        'dan': dan,
                        'od': srecanje.od,
                        'do': srecanje.do
                    },
                ))
            for rezervacija in konflikti_rezervacije(self.cleaned_data['ucilnice']):
                errors.append(forms.ValidationError(
                    'Vaša rezervacija se prekriva z rezervacijo osebe %(oseba)s, podana z razlogom %(razlog)s, na %(dan)s od %(od)i do %(do)i.',
                    params = {
                        'oseba': rezervacija.osebe.first() if rezervacija.osebe.count() >= 1 else '(neznan)',
                        'razlog': rezervacija.opomba,
                        'dan': dan,
                        'od': rezervacija.od,
                        'do': rezervacija.do
                    },
                ))
        if self.cleaned_data['do'] <= self.cleaned_data['od']:
            errors.append(forms.ValidationError('Čas trajanja rezervacije mora biti pozitiven.'))
        if errors:
            raise forms.ValidationError(errors)
        return self.cleaned_data


class RezervacijeAdminAuthenticationForm(AuthenticationForm):
    """
    Login forma za urejevalnik rezervacij. Je potrebna, saj default login
    forma zahteva status is_staff, medtem ko na /rezervacije/urejevalnik
    zahtevamo zgolj is_active (navaden uporabnik).
    """
    error_messages = {
        'invalid_login': "Prosimo, vnesite vaše %(username)s in geslo."
    }

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )
