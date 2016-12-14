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
                %for id, smer, letnik in letniki:
                <tr>
                    <td><a href="/letnik/{{id}}">{{smer}}, {{letnik}}. letnik</a></td>
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
                %for id, ime, priimek, _ in osebe:
                <tr>
                    <td><a href="/oseba/{{id}}">{{ime}} {{priimek}}</a></td>
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
                %for id, oznaka, velikost, racunalniska in ucilnice:
                <tr>
                    <td>
                        <a href="/ucilnica/{{id}}">
                            {{oznaka}}
                        </a>
                        %if racunalniska:
                        <i class="tiny material-icons">computer</i>
                        %end
                    </td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
</div>