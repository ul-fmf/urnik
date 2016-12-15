% rebase('osnova.tpl')
<div class="row">
    <div class="col s4">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Letnik</th>
                </tr>
            </thead>
            <tbody>
                %for letnik in letniki:
                <tr>
                    <td><a href="/letnik/{{letnik['id']}}">{{letnik['smer']}}, {{letnik['letnik']}}. letnik</a></td>
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
                    <td><a href="/oseba/{{oseba['id']}}">{{oseba['ime']}} {{oseba['priimek']}}</a></td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
    <div class="col s4">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Učilnica</th>
                </tr>
            </thead>
            <tbody>
                %for ucilnica in ucilnice:
                <tr>
                    <td>
                        <a href="/ucilnica/{{ucilnica['id']}}">
                            {{ucilnica['oznaka']}}
                        </a>
                        %if ucilnica['racunalniska']:
                        <i class="tiny material-icons">computer</i>
                        %end
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
</div>