from django.contrib import admin
from django.shortcuts import redirect
from .models import Oseba, Letnik, Ucilnica, Predmet, Srecanje, Rezervacija


@admin.register(Oseba)
class OsebaAdmin(admin.ModelAdmin):
    search_fields = (
        'ime',
        'priimek',
    )


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


@admin.register(Rezervacija)
class RezervacijaAdmin(admin.ModelAdmin):
    list_display = (
        'seznam_ucilnic',
        'seznam_oseb',
        'dan',
        'od',
        'do',
        'opomba',
    )
    list_filter = (
        ('osebe', admin.RelatedOnlyFieldListFilter),
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
