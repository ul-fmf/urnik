from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from urnik.iskanik_konfliktov import ProsteUcilnice, IskalnikKonfliktov
from urnik.utils import teden_dneva
from .models import *


def izbrani_semester(request):
    urejanje = request.session.get('urejanje', False)
    kljuc_semestra = 'semester_za_urejanje' if urejanje else 'semester_za_ogled'
    semester = cache.get(kljuc_semestra)
    if not semester:
        if urejanje:
            semester = Semester.objects.latest('od')
        else:
            semester = Semester.objects.filter(objavljen=True).latest('od')
        cache.set(kljuc_semestra, semester, None)
    return semester


def zacetna_stran(request):
    ucilnice = Ucilnica.objects.objavljene()
    return render(request, 'zacetna_stran.html', {
        'stolpci_smeri': [
            Letnik.objects.filter(oddelek=Letnik.MATEMATIKA),
            Letnik.objects.filter(oddelek=Letnik.FIZIKA),
        ],
        'ucilnice': ucilnice,
    })


def kombiniran_pogled_form(request):
    osebe = sorted(Oseba.objects.aktivni(), key=lambda oseba: oseba.vrstni_red())
    columns = 3
    length = len(osebe)
    per_column = length // columns
    ucilnice = Ucilnica.objects.objavljene()
    return render(request, 'kombiniran_pogled.html', {
        'stolpci_smeri': [
            Letnik.objects.filter(oddelek=Letnik.MATEMATIKA),
            Letnik.objects.filter(oddelek=Letnik.FIZIKA),
        ],
        'osebe': [osebe[i*per_column:(i+1)*per_column] for i in range(columns)],
        'ucilnice': ucilnice,
        'naslov': 'Kombiniran pogled',
    })


def rezervacije(request):
    queryset = Rezervacija.objects.prihajajoce().prefetch_related(
        'ucilnice',
        'osebe',
        'ucilnice__srecanja__ucitelji',
        'ucilnice__srecanja__predmet',
    )
    racunaj_konflikte = request.user.is_staff

    if racunaj_konflikte:
        iskalnik = IskalnikKonfliktov.za_rezervacije(queryset)

    rezervacije = []
    for rezervacija in queryset:
        for ucilnica in rezervacija.ucilnice.all():
            for dan in rezervacija.dnevi():
                rezervacije.append({
                    'ucilnica': ucilnica,
                    'osebe': rezervacija.osebe,
                    'od': rezervacija.od,
                    'do': rezervacija.do,
                    'opomba': rezervacija.opomba,
                    'dan': dan,
                    'potrjena': rezervacija.potrjena,
                    'teden': teden_dneva(dan),
                })
                if racunaj_konflikte:
                    rezervacije[-1]['konflikti'] = iskalnik.konflikti(ucilnica, dan, rezervacija.od, rezervacija.do, ignore=rezervacija)
    rezervacije.sort(key=lambda r: (r['dan'], r['ucilnica'].oznaka, r['od']))
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

    return render(request, 'nova_rezervacija.html', {'form': form, 'delno_izpolnjena': ucilnica_id is not None})


@staff_member_required
def preglej_rezervacije(request):
    rezervacije = Rezervacija.objects.prihajajoce()
    rezervacije_filter = request.GET.get('filter', 'nepotrjene')
    if rezervacije_filter != 'all':
        rezervacije = rezervacije.filter(potrjena=False)
    rezervacije = rezervacije.prefetch_related(
        'ucilnice', 'osebe').order_by('dan', 'od', 'pk')

    iskalnik = IskalnikKonfliktov.za_rezervacije(rezervacije)
    data = [{'rezervacija': r, 'konflikti': list(iskalnik.konflikti_z_rezervacijo(r))} for r in rezervacije]
    for x in data:
        x['st_konfliktov'] = sum(k.st_konfliktov for _, _, k in x['konflikti'])
    return render(request, 'preglej_rezervacije.html', {'entries': data, 'filter': rezervacije_filter})


@require_POST
@staff_member_required
def potrdi_rezervacijo(request):
    r = get_object_or_404(Rezervacija, pk=request.POST['r-pk'])
    r.potrjena = True
    r.save()
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


@require_POST
@staff_member_required
def izbrisi_rezervacijo(request):
    get_object_or_404(Rezervacija, pk=request.POST['r-pk']).delete()
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


@require_POST
@staff_member_required
def potrdi_vse_rezervacije(request):
    Rezervacija.objects.prihajajoce().filter(potrjena=False).update(potrjena=True)
    return redirect(request.POST.get('redirect') or reverse('preglej_rezervacije'))


def urnik(request, srecanja, naslov, barve=None):
    legenda = barve
    if barve is None:
        barve = Predmet.objects.filter(srecanja__in=srecanja).distinct()
    if request.user.is_staff and request.session.get('urejanje', False):
        if request.META['QUERY_STRING']:
            next_url = '{}?{}'.format(request.path, request.META['QUERY_STRING'])
        else:
            next_url = request.path
        return render(request, 'urnik.html', {
            'nacin': 'urejanje',
            'naslov': naslov,
            'srecanja': srecanja.urnik(barve=barve),
            'odlozena_srecanja': izbrani_semester(request).srecanja.odlozena(),
            'prekrivanja_po_tipih': izbrani_semester(request).srecanja.prekrivanja(),
            'next': next_url,
            'barve': barve,
        })
    else:
        return render(request, 'urnik.html', {
            'nacin': 'ogled',
            'naslov': naslov,
            'srecanja': srecanja.urnik(barve=barve),
            'barve': legenda,
        })


def urnik_osebe(request, oseba_id):
    oseba = get_object_or_404(Oseba, id=oseba_id)
    naslov = str(oseba)
    return urnik(request, oseba.vsa_srecanja(izbrani_semester(request)), naslov)


def urnik_letnika(request, letnik_id):
    letnik = get_object_or_404(Letnik, id=letnik_id)
    naslov = str(letnik)
    return urnik(request, letnik.srecanja(izbrani_semester(request)).all(), naslov)


def urnik_ucilnice(request, ucilnica_id):
    ucilnica = get_object_or_404(Ucilnica, id=ucilnica_id)
    naslov = 'Učilnica {}'.format(ucilnica.oznaka)
    return urnik(request, ucilnica.srecanja.filter(semester=izbrani_semester(request)), naslov, barve=[])


def urnik_predmeta(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id)
    naslov = str(predmet)
    return urnik(request, predmet.srecanja.filter(semester=izbrani_semester(request)), naslov)


def kombiniran_pogled(request):
    letniki = Letnik.objects.filter(id__in=request.GET.getlist('letnik'))
    osebe = Oseba.objects.filter(id__in=request.GET.getlist('oseba'))
    ucilnice = Ucilnica.objects.filter(id__in=request.GET.getlist('ucilnica'))
    srecanja_letnikov = izbrani_semester(request).srecanja.filter(predmet__letniki__in=letniki)
    srecanja_uciteljev = izbrani_semester(request).srecanja.filter(ucitelji__in=osebe)
    srecanja_slusateljev = izbrani_semester(request).srecanja.filter(predmet__slusatelji__in=osebe)
    srecanja_ucilnic = izbrani_semester(request).srecanja.filter(ucilnica__in=ucilnice)
    srecanja = (srecanja_letnikov | srecanja_uciteljev |
                srecanja_slusateljev | srecanja_ucilnic).distinct()
    return urnik(request, srecanja, 'Kombiniran pogled', barve=list(letniki) + list(osebe) + list(ucilnice))


def proste_ucilnice(request):
    teden = request.GET.get('teden', None)
    try:
        teden = parse_date(teden)
        weekday = teden.weekday()
        if weekday <= 5:
            teden -= datetime.timedelta(days=weekday)
        else:
            teden += datetime.timedelta(days=7-weekday)
    except:
        teden = None

    pokazi_zasedene = bool(request.GET.get('pz', False))

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
            proste.dodaj_srecanja_semestra(semester)
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
        'ustrezne_ucilnice': list(ucilnice),
    })


@require_POST
def proste_ucilnice_filter(request):
    tipi = [k for k in Ucilnica.OBJAVLJENI_TIPI if request.POST.get(k, '') == 'on']
    velikosti = [k for k, v in UcilnicaQuerySet.VELIKOST if request.POST.get(k, '') == 'on']
    q = QueryDict(request.POST.get('qstring', ''), mutable=True)
    q.setlist('tip', tipi)
    q.setlist('velikost', velikosti)
    response = redirect('proste')
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
        return render(request, 'urnik.html', {
            'nacin': 'premikanje',
            'naslov': 'Premikanje srečanja',
            'srecanja': srecanje.povezana_srecanja().urnik(),
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


def print_all(request):
    return render(request, 'print_all.html', {
        'naslov': 'Množično tiskanje',
        'oddelki': Letnik.ODDELEK,
        'moznosti': [('printall_ucilnice', 'učilnice'), ('printall_smeri', 'smeri')],
    })


def print_all_ucilnice(request, oddelek):
    return render(request, 'print_all_list.html', {
        'links': [reverse('urnik_ucilnice', args=[u.id]) for u in Ucilnica.objects.filter(tip=oddelek)]
    })


def print_all_smeri(request, oddelek):
    return render(request, 'print_all_list.html', {
        'links': [reverse('urnik_letnika', args=[l.id]) for l in Letnik.objects.filter(oddelek=oddelek)]
    })
