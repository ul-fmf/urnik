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
    % for ura in range(min_ura - 1, max_ura + 1):
    % bottom = (max_ura - ura) * enota_visine
    % style = 'bottom: {:.2%}'.format(bottom)
    <div class="ura" style="{{ style }}">
        {{ura if ura >= min_ura else ''}}
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
            Ime predmeta
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
    </div>
    % end
    % for (dan, ura), termin in get('prosti_termini', {}).items():
    % left = (dan - 1) * enota_sirine
    % top = (ura - min_ura) * enota_visine
    % height = enota_visine
    % width = enota_sirine
    % style = 'position: absolute; left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
    <form action="/" method="post" class="termin" style="{{style}}">
        <button class="{{termin['zasedenost']}}"></button>
    </form>
    % end
</div>
