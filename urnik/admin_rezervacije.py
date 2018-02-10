from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.actions import delete_selected as delete_selected_default
from .models import Rezervacija
from .forms import RezervacijeAdminAuthenticationForm, RezervacijaForm
from .utils import ureja_rezervacijo

class RezervacijeAdminSite(AdminSite):
    site_header = 'Urejevalnik rezervacij'

    login_form = RezervacijeAdminAuthenticationForm

    def has_permission(self, request):
        # Poleg tega je vseeno potrebno spremeniti še login formo, zgoraj
        return request.user.is_active

rezervacije_admin_site = RezervacijeAdminSite(name='rezervacije_admin_site')

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

@admin.register(Rezervacija, site=rezervacije_admin_site)
class RezervacijaAdmin(admin.ModelAdmin):
    form = RezervacijaForm
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

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True if request.user.is_active else False

    def has_module_permission(self, request):
        return True if request.user.is_active else False

    def has_change_permission(self, request, obj=None):
        # Če obj is None vrni True zato, da lahko user sploh vidi tabelo svojih rezervacij
        return True if obj is None else ureja_rezervacijo(request.user, obj)

    def delete_selected(self, request, queryset):
        if request.user.is_staff:
            return delete_selected_default(self, request, queryset)
        elif request.user.is_active:
            if not all((ureja_rezervacijo(request.user, obj)) for obj in queryset):
                raise PermissionDenied
            else:
                for obj in queryset:
                    obj.delete()
        else:
            return PermissionDenied

    actions = [delete_selected]

    def get_queryset(self, request):
        if request.user.is_staff:
            qs = super().get_queryset(request)
        else:
            qs = request.user.rezervacije
        return qs.prefetch_related(
            'ucilnice',
            'osebe',
        )
