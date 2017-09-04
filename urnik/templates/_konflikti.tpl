%for opis_tipa, prekrivanja_tipa in prekrivanja_po_tipih.items(): 
<h5><i class="material-icons">warning</i> {{opis_tipa}}</h5>
<ul class="collection">
%for (konflikt, dan, ura), srecanja in prekrivanja_tipa.items():
    <li class="collection-item">
        {{ konflikt }}
        <small><ul>
        % for srecanje in srecanja:
            <li>
                <a href="/srecanje/{{srecanje.id}}/premakni/">
                    <i class="tiny material-icons">open_with</i>
                </a>
                {{srecanje.predmet.kratica}} {{srecanje.tip}},
                % if type(konflikt).__name__ != 'Oseba' and srecanje.ucitelj:
                {{srecanje.ucitelj.priimek}},
                % end
                % if type(konflikt).__name__ != 'Ucilnica':
                {{srecanje.ucilnica.oznaka}},
                % end
                {{srecanje.ura}}–{{srecanje.ura + srecanje.trajanje}},
            </li>
        % end
        </ul></small>
    </li>
% end
</ul>
% end