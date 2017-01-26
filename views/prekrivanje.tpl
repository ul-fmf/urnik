%rebase('osnova.tpl')
<ul>
%for (ucilnica, dan, ura), srecanja in prekrivanje_ucilnic.items():
<li>
    V učilnici <a href="/urnik?ucilnica={{ucilnica}}">{{podatki_ucilnic[ucilnica]['oznaka']}}</a> so v
    {{['?', 'ponedeljek', 'torek', 'sredo', 'četrtek', 'petek'][dan]}}
    ob {{ura}}h sledeča srečanja:
    <ul>
    %for srecanje in srecanja:
    %podatki_srecanja = podatki_srecanj[srecanje]
    %podatki_osebe = podatki_oseb[podatki_srecanja['ucitelj']]
    %podatki_predmeta = podatki_predmetov[podatki_srecanja['predmet']]
        <li>
            {{podatki_osebe['ime']}} {{podatki_osebe['priimek']}},
            {{podatki_srecanja['ura']}} – {{podatki_srecanja['ura'] + podatki_srecanja['trajanje']}},
            {{{'P': 'predavanja', 'S': 'seminar', 'V': 'vaje', 'L': 'laboratorijske vaje'}[podatki_srecanja['tip']]}},
            {{podatki_predmeta['ime']}}
        </li>
    %end
    </ul>
</li>
%end
</ul>
<ul>
%for (oseba, dan, ura), srecanja in prekrivanje_oseb.items():
<li>
    <a href="/urnik?oseba={{oseba}}">{{podatki_oseb[oseba]['ime']}} {{podatki_oseb[oseba]['priimek']}}</a> ima v
    {{['?', 'ponedeljek', 'torek', 'sredo', 'četrtek', 'petek'][dan]}}
    ob {{ura}}h sledeča srečanja:
    <ul>
    %for srecanje in srecanja:
    %podatki_srecanja = podatki_srecanj[srecanje]
    %podatki_ucilnice = podatki_ucilnic[podatki_srecanja['ucilnica']]
    %podatki_predmeta = podatki_predmetov[podatki_srecanja['predmet']]
        <li>
            {{podatki_ucilnice['oznaka']}},
            {{podatki_srecanja['ura']}} – {{podatki_srecanja['ura'] + podatki_srecanja['trajanje']}},
            {{{'P': 'predavanja', 'S': 'seminar', 'V': 'vaje', 'L': 'laboratorijske vaje'}[podatki_srecanja['tip']]}},
            {{podatki_predmeta['ime']}}
        </li>
    %end
    </ul>
</li>
%end
</ul>
<ul>
%for (letnik, dan, ura), srecanja in prekrivanje_letnikov.items():
<li>
    <a href="/urnik?letnik={{letnik}}">{{podatki_letnikov[letnik]['smer']}}, {{podatki_letnikov[letnik]['leto']}}. letnik</a> ima v
    {{['?', 'ponedeljek', 'torek', 'sredo', 'četrtek', 'petek'][dan]}}
    ob {{ura}}h sledeča srečanja:
    <ul>
    %for srecanje in srecanja:
    %podatki_srecanja = podatki_srecanj[srecanje]
    %podatki_ucilnice = podatki_ucilnic[podatki_srecanja['ucilnica']]
    %podatki_osebe = podatki_oseb[podatki_srecanja['ucitelj']]
    %podatki_predmeta = podatki_predmetov[podatki_srecanja['predmet']]
        <li>
            {{podatki_osebe['ime']}} {{podatki_osebe['priimek']}},
            {{podatki_ucilnice['oznaka']}},
            {{podatki_srecanja['ura']}} – {{podatki_srecanja['ura'] + podatki_srecanja['trajanje']}},
            {{{'P': 'predavanja', 'S': 'seminar', 'V': 'vaje', 'L': 'laboratorijske vaje'}[podatki_srecanja['tip']]}},
            {{podatki_predmeta['ime']}}
        </li>
    %end
    </ul>
</li>
%end
</ul>
