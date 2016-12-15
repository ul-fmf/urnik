% rebase('osnova.tpl')
<ul>
    %for srecanje in srecanja:
    <li>
        {{['?', 'ponedeljek', 'torek', 'sreda', 'četrtek', 'petek'][srecanje['dan']]}},
        {{srecanje['ura']}}:15 – {{srecanje['ura'] + srecanje['trajanje']}}:00,
        {{srecanje['ime']}} {{srecanje['priimek']}},
        {{{'P': 'predavanja', 'S': 'seminar', 'V': 'vaje', 'L': 'laboratorijske vaje'}[srecanje['tip']]}},
        {{srecanje['oznaka']}}
    </li>
    %end
</ul>