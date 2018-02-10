from django.contrib.auth.models import User
from .models import Rezervacija

def ureja_rezervacijo(user: User, rezervacija: Rezervacija) -> bool:
    return rezervacija in user.rezervacije.all() or user.is_staff
