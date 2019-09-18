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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include

import urnik.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('rezervacije/', urnik.views.rezervacije, name='rezervacije'),
    path('nova-rezervacija/', urnik.views.nova_rezervacija, name='nova_rezervacija'),
    re_path(r'^nova-rezervacija/(?P<ucilnica_id>\d+)/(?P<ura>\d+)/(?P<teden>[0-9-]*)/(?P<dan_v_tednu>[0-6])/$',
            urnik.views.nova_rezervacija, name='nova_rezervacija_za_ucilnico'),
    path('preglej-rezervacije/', urnik.views.preglej_rezervacije, name='preglej_rezervacije'),
    path('potrdi-rezervacijo/', urnik.views.potrdi_rezervacijo, name='potrdi_rezervacijo'),
    path('potrdi-vse-rezervacije/', urnik.views.potrdi_vse_rezervacije, name='potrdi_vse_rezervacije'),
    path('izbrisi-rezervacijo/', urnik.views.izbrisi_rezervacijo, name='izbrisi_rezervacijo'),
    path('srecanje/<int:srecanje_id>/premakni/', urnik.views.premakni_srecanje, name='premakni_srecanje'),
    path('srecanje/<int:srecanje_id>/podvoji/', urnik.views.podvoji_srecanje, name='podvoji_srecanje'),
    path('srecanje/<int:srecanje_id>/odlozi/', urnik.views.odlozi_srecanje, name='odlozi_srecanje'),
    path('srecanje/<int:srecanje_id>/trajanje/', urnik.views.nastavi_trajanje_srecanja, name='nastavi_trajanje_srecanja'),
    path('preklopi_urejanje/', urnik.views.preklopi_urejanje, name='preklopi_urejanje'),
    path('izberi-semester/', urnik.views.izbira_semestra, name='izbira_semestra'),
    path('bugreport/', urnik.views.bug_report, name='bugreport'),
    path('help/', urnik.views.help_page, name='help'),
    path('', include('urnik.semester_urls'), kwargs={'semester_id': None}),
    path('semester/<int:semester_id>/', include('urnik.semester_urls'))
]
