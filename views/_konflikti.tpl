%for tip, opis in (('ucilnice', 'Konflikti učilnic'), ('osebe', 'Konflikti oseb'), ('letniki', 'Konflikti smeri')): 
<h5><i class="material-icons">warning</i> {{opis}}</h5>
<ul class="collection">
%for (dan, ura), prekrivanja_po_tipih in prekrivanja.items():
    % for id, srecanja in prekrivanja_po_tipih.get(tip, {}).items():
        <li class="collection-item">
            {{['?', 'PON', 'TOR', 'SRE', 'ČET', 'PET'][dan]}}, {{ura}}h,
            % if tip == 'ucilnice':
                {{srecanja[0]['ucilnica']['oznaka']}}:
            % elif tip == 'osebe':
                {{srecanja[0]['ucitelj']['ime']}} {{srecanja[0]['ucitelj']['priimek']}}:
            % elif tip == 'letniki':
                {{','.join([letnik['smer'] + (', ' + str(letnik['leto']) + '. letnik' if letnik['leto'] else '') for letnik in srecanja[0]['predmet']['letniki'] if letnik['id'] == id])}}:
            % end
            <small><ul>
            % for srecanje in srecanja:
                <li>
                    <a href="/uredi/srecanje/{{srecanje['id']}}/premakni/">
                        <i class="tiny material-icons">open_with</i>
                    </a>
                    {{srecanje['predmet']['kratica']}} {{srecanje['tip']}},
                    % if tip != 'osebe':
                    {{srecanje['ucitelj']['priimek']}},
                    % end
                    % if tip != 'ucilnice':
                    {{srecanje['ucilnica']['oznaka']}},
                    % end
                    {{srecanje['ura']}}–{{srecanje['ura'] + srecanje['trajanje']}},
                </li>
            % end
            </ul></small>
        </li>
    % end
% end
</ul>
% end