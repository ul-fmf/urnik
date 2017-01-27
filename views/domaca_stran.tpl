% rebase('osnova.tpl')
<div class="row">
    <div class="col s3">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Letnik</th>
                </tr>
            </thead>
            <tbody>
                %for letnik in letniki.values():
                <tr>
                    <td>
                        <a href="/urnik?letnik={{letnik['id']}}">
                            {{letnik['smer']}}{{', {}. letnik'.format(letnik['leto']) if letnik['leto'] else ''}}
                        </a>
                        <a href="/letnik/{{letnik['id']}}/uredi">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
                <tr>
                    <td>
                        <a href="/letnik/ustvari">
                            <i class="tiny material-icons">add</i>
                            ustvari nov letnik
                        </a>
                    </td>
                </tr>
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
                %for oseba in osebe.values():
                <tr>
                    <td>
                        <a href="/urnik?oseba={{oseba['id']}}">
                            {{oseba['ime']}} {{oseba['priimek']}}
                        </a>
                        <a href="/oseba/{{oseba['id']}}/uredi">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
                <tr>
                    <td>
                        <a href="/oseba/ustvari">
                            <i class="tiny material-icons">add</i>
                            ustvari novo osebo
                        </a>
                    </td>
                </tr>
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
                %for predmet in predmeti.values():
                <tr>
                    <td>
                        <a href="/urnik?ucilnica={{predmet['id']}}">
                            {{predmet['ime']}}
                        </a>
                        %if predmet['racunalniski']:
                        <i class="tiny material-icons">computer</i>
                        %end
                        <a href="/predmet/{{predmet['id']}}/uredi">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
                <tr>
                    <td>
                        <a href="/predmet/ustvari">
                            <i class="tiny material-icons">add</i>
                            ustvari nov predmet
                        </a>
                    </td>
                </tr>
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
                %for ucilnica in ucilnice.values():
                <tr>
                    <td>
                        <a href="/urnik?ucilnica={{ucilnica['id']}}">
                            {{ucilnica['oznaka']}}
                        </a>
                        %if ucilnica['racunalniska']:
                        <i class="tiny material-icons">computer</i>
                        %end
                        <a href="/ucilnica/{{ucilnica['id']}}/uredi">
                            <i class="tiny material-icons">edit</i>
                        </a>
                    </td>
                </tr>
                %end
                <tr>
                    <td>
                        <a href="/ucilnica/ustvari">
                            <i class="tiny material-icons">add</i>
                            ustvari novo učilnico
                        </a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>