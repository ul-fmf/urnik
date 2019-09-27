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
pip install -r requirements/local.txt
```

#### Apliciraj migracije
Če boš uporabljal anonimizirano bazo, jo prej premakni v mapo `project` in preimenuj v `db.sqlite3` ter šele nato apliciraj migracije.
```
python manage.py migrate
```

#### Zaženi strežnik
```
python manage.py runserver
```
