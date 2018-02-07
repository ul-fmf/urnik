"""urnik URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import urnik.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/login/$', auth_views.login,  {'template_name': 'admin/login.html'}, name='login'),
    url(r'^$', urnik.views.zacetna_stran, name='zacetna_stran'),
    url(r'^urnik/$', urnik.views.kombiniran_pogled, name='kombiniran_pogled'),
    url(r'^kombiniran/$', urnik.views.kombiniran_pogled_form, name='kombiniran_pogled_form'),
    url(r'^rezervacije/$', urnik.views.rezervacije, name='rezervacije'),
    url(r'^proste/$', urnik.views.proste_ucilnice, name='proste'),
    url(r'^proste_filter/$', urnik.views.proste_ucilnice_filter, name='proste_filter'),
    url(r'^oseba/(?P<oseba_id>\d+)/$', urnik.views.urnik_osebe, name='urnik_osebe'),
    url(r'^letnik/(?P<letnik_id>\d+)/$', urnik.views.urnik_letnika, name='urnik_letnika'),
    url(r'^ucilnica/(?P<ucilnica_id>\d+)/$', urnik.views.urnik_ucilnice, name='urnik_ucilnice'),
    url(r'^predmet/(?P<predmet_id>\d+)/$', urnik.views.urnik_predmeta, name='urnik_predmeta'),
    url(r'^srecanje/(?P<srecanje_id>\d+)/premakni/$', urnik.views.premakni_srecanje, name='premakni_srecanje'),
    url(r'^srecanje/(?P<srecanje_id>\d+)/podvoji/$', urnik.views.podvoji_srecanje, name='podvoji_srecanje'),
    url(r'^srecanje/(?P<srecanje_id>\d+)/odlozi/$', urnik.views.odlozi_srecanje, name='odlozi_srecanje'),
    url(r'^srecanje/(?P<srecanje_id>\d+)/trajanje/$', urnik.views.nastavi_trajanje_srecanja, name='nastavi_trajanje_srecanja'),
    url(r'^preklopi_urejanje/$', urnik.views.preklopi_urejanje, name='preklopi_urejanje'),
    url(r'^bugreport/$', urnik.views.bug_report, name='bugreport'),
    url(r'^help/$', urnik.views.help_page, name='help'),
    url(r'^printall/$', urnik.views.print_all, name='printall'),
    url(r'^printall/ucilnice/(?P<oddelek>[MF])/$', urnik.views.print_all_ucilnice, name='printall_ucilnice'),
    url(r'^printall/smeri/(?P<oddelek>[MF])/$', urnik.views.print_all_smeri, name='printall_smeri'),
]

if 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
