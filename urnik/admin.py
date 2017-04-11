from django.contrib import admin
from .models import Oseba, Letnik, Ucilnica, Predmet, Srecanje


admin.site.register(Oseba)
admin.site.register(Letnik)
admin.site.register(Ucilnica)
admin.site.register(Predmet)
admin.site.register(Srecanje)
