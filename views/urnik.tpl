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
    % for ura in range(min_ura, max_ura):
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
            {{srecanje['predmet']['ime']}} {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </div>
        <div class="ucitelj">
            <a href="/urnik?oseba={{srecanje['ucitelj']['id']}}">
                {{srecanje['ucitelj']['priimek']}}
            </a>
        </div>
        <div class="ucilnica">
            <a href="/urnik?ucilnica={{srecanje['ucilnica']['id']}}">
                {{srecanje['ucilnica']['oznaka']}}
            </a>
        </div>
        <div class="urejanje">
            % if srecanje['trajanje'] > 1:
            <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] - 1}}">
                <button>
                    <i class="tiny material-icons">file_upload</i> skrajšaj
                </button>
            </form>
            % end
            <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] + 1}}">
                <button>
                    <i class="tiny material-icons">file_download</i> podaljšaj
                </button>
            </form>
            <form method="post" action="/srecanje/{{srecanje['id']}}/izbrisi">
                <button>
                    <i class="tiny material-icons">delete</i> pobriši
                </button>
            </form>
            <form method="post" action="/srecanje/{{srecanje['id']}}/podvoji">
                <button>
                    <i class="tiny material-icons">content_copy</i> podvoji
                </button>
            </form>
            <a href="/srecanje/{{srecanje['id']}}/premakni">
                <i class="tiny material-icons">open_with</i> premakni
            </a>
            <form method="post" action="/srecanje/{{srecanje['id']}}/odlozi">
                <button>
                    <i class="tiny material-icons">move_to_inbox</i> odloži
                </button>
            </form>
            <a href="/srecanje/{{srecanje['id']}}/uredi">
                <i class="tiny material-icons">edit</i> uredi
            </a>
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
        % for ucilnica in termin['ucilnice']:
            <form method="post" class="izbrana_ucilnica {{ucilnica['zasedenost']}} {{ucilnica['ustreznost']}}">
                <input type="hidden" name="next" value="{{next}}">
                <input value="{{dan}}" name="dan" type="hidden">
                <input value="{{ura}}" name="ura" type="hidden">
                <input value="{{ucilnica['id']}}" name="ucilnica" type="hidden">
                <button class="">{{ucilnica['oznaka']}}<br><small>{{ucilnica['velikost']}}</small></button>
            </form>
        % end
        </div>
    </div>
    % end
</div>
</div>
<div id='informacije'>
<h5><i class="material-icons">inbox</i> Odložišče</h5>
    % for srecanje in odlozena_srecanja:
    <div class="srecanje">
        <div class="predmet">
            {{srecanje['predmet']['ime']}} {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </div>
        <div class="ucitelj">
            <a href="/urnik?oseba={{srecanje['ucitelj']['id']}}">
                {{srecanje['ucitelj']['priimek']}}
            </a>
        </div>
        <div class="ucilnica">
            <a href="/urnik?ucilnica={{srecanje['ucilnica']['id']}}">
                {{srecanje['ucilnica']['oznaka']}}
            </a>
        </div>
        <div class="urejanje">
            % if srecanje['trajanje'] > 1:
            <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] - 1}}">
                <button>
                    <i class="tiny material-icons">file_upload</i> skrajšaj
                </button>
            </form>
            % end
            <form method="post" action="/srecanje/{{srecanje['id']}}/trajanje">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] + 1}}">
                <button>
                    <i class="tiny material-icons">file_download</i> podaljšaj
                </button>
            </form>
            <form method="post" action="/srecanje/{{srecanje['id']}}/izbrisi">
                <button>
                    <i class="tiny material-icons">delete</i> pobriši
                </button>
            </form>
            <form method="post" action="/srecanje/{{srecanje['id']}}/podvoji">
                <button>
                    <i class="tiny material-icons">content_copy</i> podvoji
                </button>
            </form>
            <a href="/srecanje/{{srecanje['id']}}/premakni">
                <i class="tiny material-icons">open_with</i> premakni
            </a>
            <a href="/srecanje/{{srecanje['id']}}/uredi">
                <i class="tiny material-icons">edit</i>
            </a>
        </div>
    </div>
    % end
<h5><i class="material-icons">warning</i> Konflikti</h5>
<ul>
%for (dan, ura), prekrivanja_po_tipih in prekrivanja.items():
    % for tip, prekrivanja in prekrivanja_po_tipih.items():
        % for id, srecanja in prekrivanja.items():
        <li>
            {{['?', 'ponedeljek', 'torek', 'sredo', 'četrtek', 'petek'][dan]}}, {{ura}}h,
            % if tip == 'ucilnice':
                {{srecanja[0]['ucilnica']['oznaka']}}:
            % elif tip == 'osebe':
                {{srecanja[0]['ucitelj']['ime']}} {{srecanja[0]['ucitelj']['priimek']}}:
            % elif tip == 'letniki':
                {{','.join([letnik['smer'] + (', ' + str(letnik['leto']) + '. letnik' if letnik['leto'] else '') for letnik in srecanja[0]['predmet']['letniki'] if letnik['id'] == id])}}:
            % end
            <ul>
            % for srecanje in srecanja:
                <li>
                    {{srecanje['predmet']['kratica']}} {{srecanje['tip']}},
                    {{srecanje['ucitelj']['priimek']}},
                    {{srecanje['ucilnica']['oznaka']}},
                    {{srecanje['ura']}} – {{srecanje['ura'] + srecanje['trajanje']}},
                    <a href="/srecanje/{{srecanje['id']}}/premakni">
                        <i class="tiny material-icons">open_with</i>
                    </a>
                </li>
            % end
            </ul>
        </li>
        %end
    % end
% end
</ul>
</div>
