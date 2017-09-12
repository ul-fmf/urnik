from django.contrib import admin
from django.shortcuts import redirect
from .models import Oseba, Letnik, Ucilnica, Predmet, Srecanje


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
    )
    filter_horizontal = (
        'slusatelji',
        'letniki',
    )


@admin.register(Srecanje)
class SrecanjeAdmin(admin.ModelAdmin):

    def response_change(self, request, obj):
        return redirect(request.GET.get('next', '/'))

    def response_delete(self, request, obj_display, obj_id):
        return redirect(request.GET.get('next', '/'))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'predmet',
            'ucitelj',
            'ucilnica',
        )
