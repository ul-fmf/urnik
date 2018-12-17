from django.contrib import admin, messages
from django.shortcuts import redirect
from .models import Oseba, Letnik, Ucilnica, Predmet, Srecanje, Semester, Rezervacija


@admin.register(Oseba)
class OsebaAdmin(admin.ModelAdmin):
    search_fields = (
        'ime',
        'priimek',
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = (
        'ime',
        'od',
        'do',
        'objavljen',
    )
    list_display_links = (
        'ime',
    )

    def pripravi_kopijo(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Izberite natanko en semester.')
        else:
            stari_semester = queryset.get()
            novi_semester = stari_semester.pripravi_kopijo()
            messages.success(request, 'Kopija {} je pripravljena. Preverite datume začetka in konca!'.format(novi_semester))


    pripravi_kopijo.short_description = 'Pripravi kopijo semestra'
   
    actions = [pripravi_kopijo]



@admin.register(Letnik)
class LetnikAdmin(admin.ModelAdmin):
    search_fields = (
        'smer',
    )
    list_display = (
        '__str__',
        'smer',
        'leto',
        'oddelek',
        'kratica',
    )
    list_display_links = (
        '__str__',
    )
    list_editable = (
        'smer',
        'leto',
        'oddelek',
        'kratica',
    )


@admin.register(Ucilnica)
class UcilnicaAdmin(admin.ModelAdmin):
    list_display = (
        'oznaka',
        'velikost',
        'tip',
    )
    list_filter = (
        'tip',
    )


@admin.register(Predmet)
class PredmetAdmin(admin.ModelAdmin):
    list_display = (
        'ime',
        'kratica',
        'stevilo_studentov',
        'kratice_letnikov',
    )
    filter_horizontal = (
        'slusatelji',
        'letniki',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'letniki',
        )

class CasRezervacijeListFilter(admin.SimpleListFilter):
    title = 'čas rezervacije'
    parameter_name = 'cas'

    def lookups(self, request, model_admin):
        return (
            (None, 'Prihajajoče'),
            ('vse', 'Vse'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'vse':
            return queryset
        else:
            return queryset.prihajajoce()

@admin.register(Rezervacija)
class RezervacijaAdmin(admin.ModelAdmin):
    search_fields = (
        'osebe__ime',
        'osebe__priimek',
        'ucilnice__oznaka',
        'opomba',
    )
    list_display = (
        'seznam_ucilnic',
        'seznam_oseb',
        'dan',
        'od',
        'do',
        'opomba',
    )
    date_hierarchy = 'dan'
    list_filter = (
        CasRezervacijeListFilter,
        'ucilnice__tip',
        ('ucilnice', admin.RelatedOnlyFieldListFilter),
    )
    filter_horizontal = (
        'ucilnice',
        'osebe',
    )

    def seznam_oseb(self, obj):
        return ', '.join(str(oseba) for oseba in obj.osebe.all())
    seznam_oseb.short_description = 'Osebe'
    seznam_oseb.admin_order_field = 'osebe'

    def seznam_ucilnic(self, obj):
        return ', '.join(str(ucilnica) for ucilnica in obj.ucilnice.all())
    seznam_ucilnic.short_description = 'Učilnice'
    seznam_ucilnic.admin_order_field = 'ucilnice'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'ucilnice',
            'osebe',
        )

@admin.register(Srecanje)
class SrecanjeAdmin(admin.ModelAdmin):
    list_filter = (
        'semester',
    )
    filter_horizontal = (
        'ucitelji',
    )

    def response_change(self, request, obj):
        return redirect(request.GET.get('next', '/'))

    def response_delete(self, request, obj_display, obj_id):
        return redirect(request.GET.get('next', '/'))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'predmet',
            'ucilnica',
        ).prefetch_related(
            'ucitelji'
        )
