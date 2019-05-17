Urniki na fakulteti za matematiko in fiziko
===========================================

Navodila za razvijalce
----------------------
#### Prenesi repozitorij ali naredi fork
```
git clone git@github.com:ul-fmf/urnik.git
```
#### Naredi virtualno okolje in ga aktiviraj
```
python3 -m venv venv3
source venv3/bin/activate
```

Če oporabljaš operacijski sistem Windows, potem virtualno okolje aktiviraš z ukazom
```
venv3\Scripts\activate
```

#### Namesti potrebne pakete
```
pip install -r requirements.txt
```

Če uporabljaš operacijski sistem Windows in pri inštalaciji naletiš na napako, ki se pritožuje nad mankajočo datoteko 
pri namestitvi paketa ``python_ldap``, je težava v manjkajočih prevajalnikih. To lahko rešiš tako, da na neuradni
[spletni strani](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyldap), ki ponuja že zgrajene knjižnice, preneseš ustrezno 
za svoj operacijski sistem in jo naložiš z ukazom: 
``pip install pyldap‑2.4.45‑cp37‑cp37m‑win_amd64.whl``

Pazi, da pri tem `37` in `amd64` zamenjaš z ustrezno verzijo in arhitekturo pythona v virtualnem okolju.


#### Apliciraj migracije
Če boš uporabljal anonimizirano bazo, jo prej premakni v mapo `project` in preimenuj v `db.sqlite3` ter šele nato apliciraj migracije.
```
python manage.py migrate
```

#### Zaženi strežnik
```
python manage.py runserver
```
Da bo pri zagonu vse teklo gladko si pripravi še prazno datoteko z geslom za ldap, ki je za lokalni razvoj ne rabiš,
na strežniku pa je potrebna. Naredi prazno datoteko ``ldap_password.txt`` v glavni mapi projekta (zraven `manage.py` ).