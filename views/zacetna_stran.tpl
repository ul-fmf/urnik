% rebase('osnova.tpl')
% if nacin == 'urejanje':

<div class="row">
    <div class="col s3">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Letnik</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <a href="/uredi/letnik/ustvari/">
                            <i class="tiny material-icons">add</i>
                            ustvari nov letnik
                        </a>
                    </td>
                </tr>
                %for letnik in letniki.values():
                <tr>
                    <td>
                        <a href="/uredi/urnik?letnik={{letnik['id']}}">
                            {{letnik['smer']}}{{', {}. letnik'.format(letnik['leto']) if letnik['leto'] else ''}}
                        </a>
                        <a href="/uredi/letnik/{{letnik['id']}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
    <div class="col s3">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Oseba</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <a href="/uredi/oseba/ustvari/">
                            <i class="tiny material-icons">add</i>
                            ustvari novo osebo
                        </a>
                    </td>
                </tr>
                %for oseba in osebe.values():
                <tr>
                    <td>
                        <a href="/uredi/urnik?oseba={{oseba['id']}}">
                            {{oseba['ime']}} {{oseba['priimek']}}
                        </a>
                        <a href="/uredi/oseba/{{oseba['id']}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
    <div class="col s4">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Predmet</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <a href="/uredi/predmet/ustvari/">
                            <i class="tiny material-icons">add</i>
                            ustvari nov predmet
                        </a>
                    </td>
                </tr>
                %for predmet in predmeti.values():
                <tr>
                    <td>
                        <a href="/uredi/urnik?predmet={{predmet['id']}}">
                            {{predmet['ime']}}
                        </a>
                        <small>
                            {{predmet['kratica']}} /
                            {{predmet['stevilo_studentov'] or '?'}} /
                        {{', '.join((str(letnik['leto']) + 'L ' if letnik['leto'] else '') + letnik['smer'] for letnik in predmet['letniki'] )}}</small>
                        <a href="/uredi/predmet/{{predmet['id']}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
    <div class="col s2">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Učilnica</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <a href="/uredi/ucilnica/ustvari/">
                            <i class="tiny material-icons">add</i>
                            ustvari novo učilnico
                        </a>
                    </td>
                </tr>
                %for ucilnica in ucilnice.values():
                <tr>
                    <td>
                        <a href="/uredi/urnik?ucilnica={{ucilnica['id']}}" class="{{'skrita' if ucilnica['skrita'] else ''}}">
                            {{ucilnica['oznaka']}}
                        </a>
                        <small>{{ucilnica['velikost'] if ucilnica['velikost'] else '?'}}</small>
                        %if ucilnica['racunalniska']:
                        <i class="tiny material-icons">computer</i>
                        %end
                        <a href="/uredi/ucilnica/{{ucilnica['id']}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
</div>

% else:

<div class="container">
<div class="row">
    % for stolpec in stolpci_smeri:
    <div class="col s3">
        <table class="highlight">
            % for smer in stolpec:
            <thead>
                <tr>
                    <th>{{smer['ime']}}</th>
                </tr>
            </thead>
            <tbody>
                % for letnik in smer['letniki']:
                <tr>
                    <td style="padding: 5px">
                        <a href="/letnik/{{letnik['id']}}/">{{letnik['opis']}}</a>
                    </td>
                </tr>
                % end
            </tbody>
            % end
        </table>
    </div>
    % end
    <div class="col s2">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Učilnica</th>
                </tr>
            </thead>
            <tbody>
                %for ucilnica in ucilnice:
                <tr>
                    <td style="padding: 5px">
                        <a href="/ucilnica/{{ucilnica['id']}}/">
                            {{ucilnica['oznaka']}}
                        </a>
                        <small>
                        %if ucilnica['racunalniska']:
                        <i class="tiny material-icons">computer</i>
                        %end
                        ({{ucilnica['velikost'] or '?'}} mest)</small>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
    <div class="col s4">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Oseba</th>
                </tr>
            </thead>
            <tbody>
                %for oseba in osebe:
                <tr>
                    <td style="padding: 5px">
                        <a href="/oseba/{{oseba['id']}}/">
                            {{oseba['ime']}} <strong>{{oseba['priimek']}}</strong>
                        </a>
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
</div>
</div>

% end