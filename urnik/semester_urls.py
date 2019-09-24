from django.urls import path, re_path, include

import urnik.views

urlpatterns = [
    path('', urnik.views.zacetna_stran, name='zacetna_stran'),
    path('urnik/', urnik.views.kombiniran_pogled, name='kombiniran_pogled'),
    path('kombiniran/', urnik.views.kombiniran_pogled_form, name='kombiniran_pogled_form'),
    path('proste/', urnik.views.proste_ucilnice, name='proste'),
    path('proste_filter/', urnik.views.proste_ucilnice_filter, name='proste_filter'),
    path('oseba/<int:oseba_id>/', urnik.views.urnik_osebe, name='urnik_osebe'),
    path('letnik/<int:letnik_id>/', urnik.views.urnik_letnika, name='urnik_letnika'),
    path('ucilnica/<int:ucilnica_id>/', urnik.views.urnik_ucilnice, name='urnik_ucilnice'),
    path('predmet/<int:predmet_id>/', urnik.views.urnik_predmeta, name='urnik_predmeta'),
    path('printall/', urnik.views.print_all, name='printall'),
    re_path(r'^printall/ucilnice/(?P<oddelek>[MF])/$', urnik.views.print_all_ucilnice, name='printall_ucilnice'),
    re_path(r'^printall/smeri/(?P<oddelek>[MF])/$', urnik.views.print_all_smeri, name='printall_smeri'),
]
