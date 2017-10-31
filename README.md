Urniki na fakulteti za matematiko in fiziko
===========================================

Namen
-----

Trenutni [program](http://www-lp.fmf.uni-lj.si/urnik/urnik.htm) za izdelavo in
prikaz urnikov na FMF je že malo v letih, zato bomo poskusili narediti novega.
Program bo podpiral:

- prikaz urnikov za posamezen letnik/predavalnico/predavatelja
- urejanje urnikov
- izračun morebitnih prekrivanj
- uvoz starih urnikov

Program ne bo podpiral:

- avtomatičnega ustvarjanja urnikov iz omejitev
- urnikov, ki se znotraj semestra spreminjajo

Na kaj je treba paziti
----------------------

Ista skupina je lahko na več smereh in letnikih.

Želje uporabnikov urnika
------------------------

Povezave med urniki (če klikneš na osebo, dobiš njegov urnik, če klikneš na
predmet, greš na spletno učilnico, če klikneš na predavalnico, dobiš njen urnik)

Želje sestavljalcev urnika
--------------------------

1. Program naj sproti preverja in opozarja, če je kje prišlo do prekrivanja,
vendar naj prekrivanje vseeno dopusti (npr. če nekdo včasih uporablja običajno,
včasih pa računalniško učilnico). Prav tako naj program omogoča označevanje
neškodljivih prekrivanj (po 20 učiteljev ima na urniku hkrati isti seminar).
Dobro bi bilo, če bi imel urnik tudi neko odlagalno površino, na katero se
da skupine brez določene ure.

2. Običajno se urnik sestavi s spreminjanjem obstoječega urnika. Pri tem
običajno prihaja do sledečih sprememb:

- sprememba izvajalca:
  to bi bilo najbolj enostavno tako, da dobiš spustni meni in tam izbereš
  novega. Izvajalcev je veliko, zato je treba izbor smiselno zožati. Dobro bi
  bilo tudi, če bi večino sprememb izvajalcev program ugotovil že sam
- sprememba predavalnice:
  tudi tu bi dobil spustni meni, vendar verjetno samo prostih predavalnic
- sprememba termina:
  to bi bilo najbolj enostavno narediti tako, da skupino odvlečeš z miško,
  vendar bi moral biti opozorjen, kje je prostor. Torej, z rdečo naj bo
  pobarvano, kje je predavatelj zaseden, v prostih terminih pa naj kaže, katere
  predavalnice so proste, po možnosti samo tiste, ki so večje ali enako velike
  od trenutne. Prav tako mogoče želiš premakniti le eno uro od treh.

3. Program naj smiselno omogoča delo večim sestavljalcem (ali naj ga prepreči
ali pa prikaže, kaj dela drugi).

4. Dobro bi bilo, če bi lahko osebni urnik urejal vsak sam.

Navodila za razvijalce
----------------------
Prenesi repozitorij ali naredi fork
```
git clone git@github.com:ul-fmf/urnik.git
```
Naredi virtualno okolje in ga aktiviraj
```
python3 -m venv venv3
source venv3/bin/activate
```
Namesti potrebne pakete
```
pip install -r requirements.txt
```
Apliciraj migracije
```
python manage.py migrate
```
Zaženi strežnik
```
python manage.py runserver
```
