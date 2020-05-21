from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from urnik.iskanik_konfliktov import ProsteUcilnice, IskalnikKonfliktov
from .forms import KombiniranPogledForm, RezevacijeForm
from .models import *
from .tedenski_urnik import TedenskiUrnik
from .utils import normaliziraj_teden


def izbrani_semester_id(request):
    return request.resolver_match.kwargs.get('semester_id', None)


def izbrani_semester(request):
    if request.session.get('urejanje', False):
        return Semester.objects.latest('od')
    semester_id = izbrani_semester_id(request)
    if semester_id:
        try:
            return Semester.objects.get(pk=semester_id)
        except:
            pass
    try:
        return Semester.objects.filter(objavljen=True).latest('od')
    except Semester.DoesNotExist:
        raise ValueError("Za uporabo aplikacije dodajte v bazo vsaj en objavljen semester.")


def ogled_starega_semestra(request):
    urejanje = request.session.get('urejanje', False)
    semester_id = izbrani_semester_id(request)
    return not urejanje and semester_id is not None and \
        Semester.objects.filter(objavljen=True).latest('od').pk != semester_id


def zacetna_stran(request, semester_id=None):
    return render(request, 'zacetna_stran.html', {
        'stolpci_smeri': [
            Letnik.objects.filter(oddelek=Letnik.MATEMATIKA),
            Letnik.objects.filter(oddelek=Letnik.FIZIKA),
        ],
        'ucilnice': Ucilnica.objects.objavljene(),
    })


def izbira_semestra(request):
    semestri = Semester.objects.filter(objavljen=True)
    return render(request, 'izbira_semestra.html', {
        'semestri': semestri,
        'naslov': 'Ogled starejših urnikov'
    })


def kombiniran_pogled_form(request, semester_id=None):
    ucilnice = Ucilnica.objects.objavljene()
    form = KombiniranPogledForm()
    return render(request, 'kombiniran_pogled.html', {
        'stolpci_smeri': [
            Letnik.objects.filter(oddelek=Letnik.MATEMATIKA),
            Letnik.objects.filter(oddelek=Letnik.FIZIKA),
        ],
        'form': form,
        'ucilnice': ucilnice,
        'naslov': 'Kombiniran pogled',
    })


def rezervacije(request):
    queryset = Rezervacija.objects.prihajajoce().prefetch_related(
        Prefetch('ucilnice', to_attr='seznam_ucilnic'),
        Prefetch('osebe', to_attr='seznam_oseb'),
        Prefetch('predmeti', queryset=Predmet.objects.prefetch_related('letniki'), to_attr='seznam_predmetov'),
    )
    racunaj_konflikte = request.user.is_staff
    if racunaj_konflikte:
        iskalnik = IskalnikKonfliktov.za_rezervacije(queryset)

    rezervacije = []
    for rezervacija in queryset:
        for ucilnica in rezervacija.seznam_ucilnic:
            for dan in rezervacija.prihajajoci_dnevi():
                rezervacije.append({
                    'id': rezervacija.id,
                    'ucilnica': ucilnica,
                    'osebe': rezervacija.seznam_oseb,
                    'predmeti': rezervacija.seznam_predmetov,
                    'od': rezervacija.od,
                    'do': rezervacija.do,
                    'opomba': rezervacija.opomba,
                    'dan': dan,
                    'potrjena': rezervacija.potrjena,
                    'teden': teden_dneva(dan),
                })
                if racunaj_konflikte:
                    rezervacije[-1]['konflikti'] = iskalnik.konflikti(ucilnica, dan, rezervacija.od, rezervacija.do, ignore=rezervacija)
    rezervacije.sort(key=lambda r: (r['dan'], r['ucilnica'], r['od']))
    return render(request, 'rezervacije.html', {
        'naslov': 'Rezervacije učilnic',
        'rezervacije': rezervacije,
    })


@login_required
def nova_rezervacija(request, ucilnica_id=None, ura=None, teden=None, dan_v_tednu=None):
    if request.method == 'POST':
        form = RezevacijeForm(request.POST, dovoli_prekrivanja=True)
        if form.is_valid():
            rezervacija = form.save(commit=False)
            rezervacija.avtor_rezervacije = request.user
            rezervacija.save()
            form.save_m2m()
            return render(request, 'uspesna_rezervacija.html', {'rezervacija': rezervacija})

        # če so edine napake prekrivanja, omogočimo uporabniku, da vseeno rezervira
        if all(error.code == RezevacijeForm.PREKRIVANJA
               for _, error_list in form.errors.as_data().items() for error in error_list):
            form = RezevacijeForm(request.POST, dovoli_prekrivanja=True)
        else:
            form = RezevacijeForm(request.POST, dovoli_prekrivanja=False)

    else:
        form = RezevacijeForm()
        try:
            form.fields['osebe'].initial = [request.user.oseba]
        except Oseba.DoesNotExist:
            pass
        if ucilnica_id:
            form.fields['ucilnice'].initial = [ucilnica_id]
            try:
                ura = int(ura)
                form.fields['od'].initial = ura
                form.fields['do'].initial = ura+1
            except: pass
            try:
                teden = datetime.datetime.strptime(teden, "%Y-%m-%d")
                teden += datetime.timedelta(days=int(dan_v_tednu)-1)
                form.fields['dan'].initial = teden.strftime('%d. %m. %Y').lstrip('0').replace('. 0', '. ')
            except: pass

    return render(request, 'nova_rezervacija.html', {
        'naslov': 'Nova rezervacija',
        'form': form,
        'delno_izpolnjena': ucilnica_id is not None,
    })


@login_required
def preglej_rezervacije(request):
    if not request.user.is_staff:
        redirect('preglej_rezervacije_oseba', request.user.pk)
    rezervacije = Rezervacija.objects.prihajajoce().select_related('avtor_rezervacije')
    rezervacije_filter = request.GET.get('filter', 'nepotrjene')
    if rezervacije_filter != 'all':
        rezervacije = rezervacije.filter(potrjena=False)
    rezervacije = rezervacije.prefetch_related(
        Prefetch('ucilnice', to_attr='seznam_ucilnic'),
        Prefetch('osebe', to_attr='seznam_oseb'),
        Prefetch('predmeti', queryset=Predmet.objects.prefetch_related('letniki'), to_attr='seznam_predmetov'),
    ).order_by('dan', 'od', 'pk')
    iskalnik = IskalnikKonfliktov.za_rezervacije(rezervacije)
    data = [{'rezervacija': r, 'konflikti': list(iskalnik.konflikti_z_rezervacijo(r))} for r in rezervacije]
    for x in data:
        x['st_konfliktov'] = sum(k.st_konfliktov for _, _, k in x['konflikti'])

    return render(request, 'preglej_rezervacije.html', {
        'naslov': 'Pregled rezervacij',
        'entries': data,
        'filter': rezervacije_filter
    })


@login_required
def preglej_rezervacije_oseba(request, oseba_id):
    oseba = get_object_or_404(Oseba, pk=oseba_id)
    rezervacije = Rezervacija.objects.prihajajoce().filter(osebe=oseba).select_related(
        'avtor_rezervacije'
    ).prefetch_related(
        Prefetch('predmeti', queryset=Predmet.objects.prefetch_related('letniki'), to_attr='seznam_predmetov'),
        Prefetch('osebe', to_attr='seznam_oseb'),
        Prefetch('ucilnice', to_attr='seznam_ucilnic'),
    )
    iskalnik = IskalnikKonfliktov.za_rezervacije(rezervacije)
    data = [{'rezervacija': r, 'konflikti': list(iskalnik.konflikti_z_rezervacijo(r))} for r in rezervacije]
    for x in data:
        x['st_konfliktov'] = sum(k.st_konfliktov for _, _, k in x['konflikti'])

    return render(request, 'moje_rezervacije.html', {
        'naslov': 'Moje rezervacije',
        'oseba': oseba,
        'entries': data,
        'has_manage_perms': hasattr(request.user, 'oseba') and request.user.oseba == oseba
    })


@require_POST
@staff_member_required
def potrdi_rezervacijo(request):
    r = get_object_or_404(Rezervacija, pk=request.POST['r-pk'])
    r.potrjena = True
    r.save()
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


@require_POST
@login_required
def izbrisi_rezervacijo(request):
    rezervacija = get_object_or_404(Rezervacija, pk=request.POST['r-pk'])
    if not request.user.is_staff and request.user not in rezervacija.osebe.all():
        raise PermissionDenied
    rezervacija.delete()
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


@require_POST
@staff_member_required
def potrdi_vse_rezervacije(request):
    Rezervacija.objects.prihajajoce().filter(potrjena=False).update(potrjena=True)
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


def urnik(request, srecanja, rezervacije, naslov, teden=None, legenda=None):
    kategorije = legenda
    if kategorije is None:
        kategorije = Predmet.objects.filter(srecanja__in=srecanja).distinct()
    semester = izbrani_semester(request)
    teden_v_napacnem_semestru = False
    tedenski_urnik = TedenskiUrnik()
    tedenski_urnik.dodaj_srecanja(srecanja.za_urnik())
    if teden:
        tedenski_urnik.dodaj_rezervacije(rezervacije.za_urnik(), teden)
    if request.user.is_staff and request.session.get('urejanje', False):
        next_url = request.get_full_path()
        return render(request, 'urnik.html', {
            'nacin': 'urejanje',
            'naslov': naslov,
            'termini': tedenski_urnik.termini(kategorije),
            'odlozena_srecanja': semester.srecanja.odlozena(),
            'prekrivanja_po_tipih': semester.srecanja.prekrivanja(),
            'next': next_url,
            'legenda': legenda,
        })
    else:
        WEEK = datetime.timedelta(days=7)
        trenuten_teden = teden_dneva(datetime.date.today())
        mozni_tedni = set(t for t in semester.tedni() if t >= trenuten_teden)
        izbran_teden = teden_dneva(teden or datetime.date.today())
        for t in range(-2, 8):
            mozni_tedni.add((izbran_teden[0] + t*WEEK,
                             izbran_teden[1] + t*WEEK))
        if teden:
            semestri = Semester.objects.v_obdobju(teden, teden + WEEK)
            teden_v_napacnem_semestru = any(s != semester for s in semestri)

        return render(request, 'urnik.html', {
            'nacin': 'ogled',
            'naslov': naslov,
            'termini': tedenski_urnik.termini(kategorije),
            'legenda': legenda,
            'izbran_teden': teden,
            'trenuten_teden': trenuten_teden[0],
            'mozni_tedni': sorted(mozni_tedni),
            'teden_v_napacnem_semestru': teden_v_napacnem_semestru,
        })


def urnik_osebe(request, oseba_id, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    oseba = get_object_or_404(Oseba, id=oseba_id)
    rezervacije = Rezervacija.objects.none() if not teden else oseba.rezervacije.v_tednu(teden)
    naslov = str(oseba)
    semester = izbrani_semester(request)
    srecanja = oseba.vsa_srecanja(semester).v_tednu_semestra(teden, semester)
    return urnik(request, srecanja, rezervacije, naslov, teden)


def urnik_letnika(request, letnik_id, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    letnik = get_object_or_404(Letnik, id=letnik_id)
    rezervacije = Rezervacija.objects.none() if not teden else Rezervacija.objects.filter(predmeti__letniki=letnik).v_tednu(teden)
    naslov = str(letnik)
    semester = izbrani_semester(request)
    srecanja = letnik.srecanja(semester).all().v_tednu_semestra(teden, semester)
    return urnik(request, srecanja, rezervacije, naslov, teden)


def urnik_ucilnice(request, ucilnica_id, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    ucilnica = get_object_or_404(Ucilnica, id=ucilnica_id)
    rezervacije = Rezervacija.objects.none() if not teden else ucilnica.rezervacije.v_tednu(teden)
    naslov = 'Učilnica {}'.format(ucilnica.oznaka)
    semester = izbrani_semester(request)
    srecanja = ucilnica.srecanja.filter(semester=semester).v_tednu_semestra(teden, semester)
    return urnik(request, srecanja, rezervacije, naslov, teden, legenda=[])


def urnik_predmeta(request, predmet_id, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    predmet = get_object_or_404(Predmet, id=predmet_id)
    rezervacije = Rezervacija.objects.none() if not teden else predmet.rezervacije.v_tednu(teden)
    naslov = str(predmet)
    semester = izbrani_semester(request)
    srecanja = predmet.srecanja.filter(semester=semester).v_tednu_semestra(teden, semester)
    return urnik(request, srecanja, rezervacije, naslov, teden)


def kombiniran_pogled(request, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    letniki = Letnik.objects.filter(id__in=request.GET.getlist('letnik'))
    osebe = Oseba.objects.filter(id__in=request.GET.getlist('oseba'))
    ucilnice = Ucilnica.objects.filter(id__in=request.GET.getlist('ucilnica'))
    predmeti = Predmet.objects.filter(id__in=request.GET.getlist('predmet'))
    semester = izbrani_semester(request)

    srecanja_letnikov = semester.srecanja.filter(predmet__letniki__in=letniki)
    srecanja_uciteljev = semester.srecanja.filter(ucitelji__in=osebe)
    srecanja_slusateljev = semester.srecanja.filter(predmet__slusatelji__in=osebe)
    srecanja_ucilnic = semester.srecanja.filter(ucilnica__in=ucilnice)
    srecanja_predmetov = semester.srecanja.filter(predmet__in=predmeti)

    rezervacije = Rezervacija.objects.none()

    if teden:
        srecanja_letnikov = srecanja_letnikov.v_tednu_semestra(teden, semester)
        srecanja_uciteljev = srecanja_uciteljev.v_tednu_semestra(teden, semester)
        srecanja_slusateljev = srecanja_slusateljev.v_tednu_semestra(teden, semester)
        srecanja_ucilnic = srecanja_ucilnic.v_tednu_semestra(teden, semester)
        srecanja_predmetov = srecanja_predmetov.v_tednu_semestra(teden, semester)

        rezervacije_letnikov = Rezervacija.objects.filter(predmeti__letniki__in=letniki).v_tednu(teden)
        rezervacije_ucilnic = Rezervacija.objects.filter(ucilnice__in=ucilnice).v_tednu(teden)
        rezervacije_oseb = Rezervacija.objects.filter(osebe__in=osebe).v_tednu(teden)
        rezervacije_slusateljev = Rezervacija.objects.filter(predmeti__slusatelji__in=osebe).v_tednu(teden)
        rezervacije_predmetov = Rezervacija.objects.filter(predmeti__in=predmeti).v_tednu(teden)
        rezervacije = (rezervacije_letnikov | rezervacije_ucilnic | rezervacije_oseb | rezervacije_predmetov | rezervacije_slusateljev).distinct()

    srecanja = (srecanja_letnikov | srecanja_uciteljev |
                srecanja_slusateljev | srecanja_ucilnic | srecanja_predmetov).distinct()

    return urnik(request, srecanja, rezervacije, naslov='Kombiniran pogled', teden=teden, legenda=list(letniki) + list(osebe) + list(ucilnice) + list(predmeti))


def proste_ucilnice(request, semester_id=None):
    teden = normaliziraj_teden(request.GET.get('teden', None))
    pokazi_zasedene = int(request.GET.get('pz', 0))

    ucilnice = request.GET.getlist('ucilnica')
    if ucilnice:
        ucilnice = Ucilnica.objects.objavljene().filter(pk__in=ucilnice)
        if not ucilnice.exists():
            ucilnice = Ucilnica.objects.objavljene()
    else:
        ucilnice = Ucilnica.objects.objavljene()

    tip = set(request.GET.getlist('tip'))
    tip &= set(Ucilnica.OBJAVLJENI_TIPI)
    if not tip: tip = set(Ucilnica.OBJAVLJENI_TIPI)

    velikost = set(request.GET.getlist('velikost'))
    velikost &= {v[0] for v in UcilnicaQuerySet.VELIKOST}
    if not velikost: velikost = None

    semester = izbrani_semester(request)
    proste = ProsteUcilnice(ucilnice.filter(tip__in=tip).ustrezne_velikosti(velikost))
    if teden:
        proste.upostevaj_rezervacije_za_teden(teden)
        # teh semestrov bi moralo biti 0 ali 1
        for semester in Semester.objects.v_obdobju(teden, teden + datetime.timedelta(days=5)):
            proste.dodaj_srecanja_semestra(semester, teden)
    else:
        proste.dodaj_srecanja_semestra(semester)

    termini = proste.dobi_termine()
    for t in termini:
        t.filtriraj_ucilnice(pokazi_zasedene=pokazi_zasedene)

    now = datetime.date.today()
    mozni_tedni = set(teden_dneva(d) for r in Rezervacija.objects.prihajajoce() for d in r.dnevi() if d >= now)
    mozni_tedni.update(semester.prihodnji_tedni())
    return render(request, 'proste_ucilnice.html', {
        'naslov': 'Proste učilnice',
        'termini': termini,

        # get parameters
        'pokazi_zasedene': pokazi_zasedene,
        'velikosti': velikost,
        'tipi': [] if tip == set(Ucilnica.OBJAVLJENI_TIPI) else tip,
        'teden': teden,

        # possible values
        'mozne_velikosti_ucilnic': UcilnicaQuerySet.VELIKOST,
        'mozni_tipi_ucilnic': [u for u in Ucilnica.TIP if u[0] in Ucilnica.OBJAVLJENI_TIPI],
        'mozni_tedni': sorted(mozni_tedni),
    })


@require_POST
def proste_ucilnice_filter(request, semester_id=None):
    tipi = [k for k in Ucilnica.OBJAVLJENI_TIPI if request.POST.get(k, '') == 'on']
    velikosti = [k for k, v in UcilnicaQuerySet.VELIKOST if request.POST.get(k, '') == 'on']
    q = QueryDict(request.POST.get('qstring', ''), mutable=True)
    q.setlist('tip', tipi)
    q.setlist('velikost', velikosti)
    response = redirect(reverse('proste', kwargs={'semester_id': semester_id}))
    response['Location'] += "?" + q.urlencode()
    return response


@staff_member_required
def premakni_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    if request.method == 'POST':
        dan = int(request.POST['dan'])
        ura = int(request.POST['ura'])
        ucilnica = get_object_or_404(Ucilnica, id=request.POST['ucilnica'])
        srecanje.premakni(dan, ura, ucilnica)
        return redirect(request.POST['next'])
    else:
        tedenski_urnik = TedenskiUrnik()
        tedenski_urnik.dodaj_srecanja(srecanje.povezana_srecanja().za_urnik())
        return render(request, 'urnik.html', {
            'nacin': 'premikanje',
            'naslov': 'Premikanje srečanja',
            'srecanja': tedenski_urnik.termini(),
            'odlozena_srecanja': izbrani_semester(request).srecanja.odlozena(),
            'prekrivanja_po_tipih': {},
            'prosti_termini': srecanje.prosti_termini(request.GET['tip'], 'MAT' if 'matematika' in ','.join(
                group.name for group in request.user.groups.all()) else 'FIZ'),
            'premaknjeno_srecanje': srecanje,
            'next': request.META.get('HTTP_REFERER', reverse('zacetna_stran')),
        })


@staff_member_required
def podvoji_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.podvoji()
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@staff_member_required
def odlozi_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.odlozi()
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@staff_member_required
def nastavi_trajanje_srecanja(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    trajanje = int(request.POST['trajanje'])
    srecanje.nastavi_trajanje(trajanje)
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


@staff_member_required
def preklopi_urejanje(request):
    request.session['urejanje'] = not request.session.get('urejanje', False)
    return redirect(request.META.get('HTTP_REFERER', reverse('zacetna_stran')))


def bug_report(request):
    return render(request, 'bugreport.html', {
        'naslov': 'Prijavi napako',
    })


def help_page(request):
    return render(request, 'help.html', {
        'naslov': 'Navodila in pomoč',
    })


def print_all(request, semester_id=None):
    return render(request, 'print_all.html', {
        'naslov': 'Množično tiskanje',
        'oddelki': Letnik.ODDELEK,
        'moznosti': [('printall_ucilnice', 'učilnice'), ('printall_smeri', 'smeri')],
    })


def print_all_ucilnice(request, oddelek, semester_id=None):
    return render(request, 'print_all_list.html', {
        'links': [reverse('urnik_ucilnice', kwargs={'ucilnica_id': u.id, 'semester_id': semester_id}) for u in Ucilnica.objects.filter(tip=oddelek)]
    })


def print_all_smeri(request, oddelek, semester_id=None):
    return render(request, 'print_all_list.html', {
        'links': [reverse('urnik_letnika', kwargs={'letnik_id': l.id, 'semester_id': semester_id}) for l in Letnik.objects.filter(oddelek=oddelek)]
    })
