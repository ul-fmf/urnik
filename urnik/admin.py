from django.contrib import admin
from django.shortcuts import redirect
from .models import Oseba, Letnik, Ucilnica, Predmet, Srecanje, Semester, Rezervacija
from .admin_rezervacije import RezervacijaAdmin

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

admin.site.register(Rezervacija, RezervacijaAdmin)
