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
from django.conf.urls import url
from django.contrib import admin
import urnik.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', urnik.views.zacetna_stran, name='zacetna_stran'),
    url(r'^oseba/(?P<oseba_id>\d+)/$', urnik.views.urnik_osebe, name='urnik_osebe'),
    url(r'^letnik/(?P<letnik_id>\d+)/$', urnik.views.urnik_letnika, name='urnik_letnika'),
    url(r'^ucilnica/(?P<ucilnica_id>\d+)/$', urnik.views.urnik_ucilnice, name='urnik_ucilnice'),
    url(r'^predmet/(?P<predmet_id>\d+)/$', urnik.views.urnik_predmeta, name='urnik_predmeta'),
]
