% rebase('osnova.tpl', domov='/')

% min_ura, max_ura = 7, 20
% enota_visine = 1 / (max_ura - min_ura)
% dnevi = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
% enota_sirine = 1 / len(dnevi)

<div id="urnik" class="{{ 'cel' if nacin == 'ogled' else '' }}">
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

% if nacin == 'urejanje' or nacin == 'premikanje':

<div id="srecanja">
    % for srecanje in srecanja:
    % include('_srecanje.tpl', nacin='urejanje')
    % end
    % for (dan, ura), termin in get('prosti_termini', {}).items():
    % include('_prosti_termin.tpl')
    % end
</div>
% elif nacin == 'ogled':
<div id="srecanja">
    % for srecanje in srecanja:
    % include('_srecanje.tpl', nacin='ogled')
    % end
</div>
% end
</div>

% if nacin == 'urejanje' or nacin == 'premikanje':
<div id='informacije'>
% if nacin == 'urejanje':
<h5><i class="material-icons">inbox</i> Odložišče</h5>
    % for srecanje in odlozena_srecanja:
    % include('_srecanje.tpl', nacin='odlozisce')
    % end
% include('_konflikti.tpl')
% elif nacin == 'premikanje':
<h5><i class="material-icons">inbox</i> Premikanje srečanja</h5>
% include('_srecanje.tpl', nacin='odlozisce', srecanje=premaknjeno_srecanje)
</div>

% end
