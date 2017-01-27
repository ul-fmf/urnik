% rebase('osnova.tpl')

% min_ura, max_ura = 7, 20
% enota_visine = 1 / (max_ura - min_ura)
% dnevi = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
% enota_sirine = 1 / len(dnevi)

<div id="urnik">
<div id="dnevi">
    % for indeks_dneva, dan in enumerate(dnevi):
    % left = indeks_dneva * enota_sirine
    % style = 'left: {:.2%}'.format(left)
    <div class="dan" style="{{ style }}">
        {{dan}}
    </div>
    % end
</div>
<div id="ure">
    % for ura in range(min_ura, max_ura + 1):
    % bottom = (max_ura - ura) * enota_visine
    % style = 'bottom: {:.2%}'.format(bottom)
    <div class="ura" style="{{ style }}">
        <span>{{ura if ura >= min_ura else ''}}</span>
    </div>
    % end
</div>
<div id="srecanja">
    % for srecanje in srecanja:
    % left = (srecanje['dan'] - 1 + srecanje['zamik']) * enota_sirine
    % top = (srecanje['ura'] - min_ura) * enota_visine
    % height = srecanje['trajanje'] * enota_visine
    % width = srecanje['sirina'] * enota_sirine
    % style = 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
    <div class="srecanje" style="{{ style }};">
        <div class="predmet">
            {{srecanje['ime_predmeta']}} {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </div>
        <div class="ucitelj">
            <a href="/urnik?oseba={{srecanje['ucitelj']}}">
                {{srecanje['priimek_ucitelja']}}
            </a>
        </div>
        <div class="ucilnica">
            <a href="/urnik?ucilnica={{srecanje['ucilnica']}}">
                {{srecanje['oznaka_ucilnice']}}
            </a>
        </div>
        <div class="urejanje">
            <div class="right">
                <a href="/srecanje/{{srecanje['id']}}/premakni">
                    <i class="tiny material-icons">open_with</i>
                </a>
                <a href="/srecanje/{{srecanje['id']}}/uredi">
                    <i class="tiny material-icons">edit</i>
                </a>
                <form method="post" action="/srecanje/{{srecanje['id']}}/izbrisi">
                    <button>
                        <i class="tiny material-icons">delete</i>
                    </button>
                </form>
                <form method="post" action="/srecanje/{{srecanje['id']}}/podvoji">
                    <button>
                        <i class="tiny material-icons">content_copy</i>
                    </button>
                </form>
            </div>
            <div class="podaljsevanje">
                % if srecanje['trajanje'] > 1:
                <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                    <input type="hidden" name="next" value="{{next}}">
                    <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] - 1}}">
                    <button>
                        <i class="tiny material-icons">file_upload</i>
                    </button>
                </form>
                % end
                % if srecanje['ura'] + srecanje['trajanje'] < max_ura:
                <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                    <input type="hidden" name="next" value="{{next}}">
                    <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] + 1}}">
                    <button>
                        <i class="tiny material-icons">file_download</i>
                    </button>
                </form>
                % end
            </div>
        </div>
    </div>
    % end
    % import modeli
    % for (dan, ura), termin in get('prosti_termini', {}).items():
    % left = (dan - 1) * enota_sirine
    % top = (ura - min_ura) * enota_visine
    % height = enota_visine
    % width = enota_sirine
    % style = 'position: absolute; left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
    <div class="termin {{termin['zasedenost']}}" style="{{style}}">
        <div class="izbira_ucilnice">
        % for ucilnica, zasedenost in termin['ucilnice']:
            <form method="post" class="izbrana_ucilnica {{zasedenost}}">
                <input type="hidden" name="next" value="{{next}}">
                <input value="{{dan}}" name="dan" type="hidden">
                <input value="{{ura}}" name="ura" type="hidden">
                <input value="{{ucilnica}}" name="ucilnica" type="hidden">
                <button class="">{{modeli.podatki_ucilnice(ucilnica)['oznaka']}}</button>
            </form>
        % end
        </div>
    </div>
    % end
</div>
</div>
<div id='informacije'>
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
</div>
