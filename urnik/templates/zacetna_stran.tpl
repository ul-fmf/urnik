{% extends 'osnova.tpl' %}
{% block content %}
{% if nacin == 'urejanje' %}

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
                {% for letnik in letniki %}
                <tr>
                    <td>
                        <a href="/uredi/urnik?letnik={{letnik.id}}">
                            {{letnik}}
                        </a>
                        <a href="/uredi/letnik/{{letnik.id}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                        <a href="/uredi/pobrisi/letnik/{{letnik.id}}/">
                            <i class="tiny material-icons">delete</i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
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
                {% for oseba in osebe %}
                <tr>
                    <td>
                        <a href="/uredi/urnik?oseba={{oseba.id}}">
                            {{oseba.ime}} {{oseba.priimek}}
                        </a>
                        <a href="/uredi/oseba/{{oseba.id}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                        <a href="/uredi/pobrisi/oseba/{{oseba.id}}/">
                            <i class="tiny material-icons">delete</i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
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
                {% for predmet in predmeti %}
                <tr>
                    <td>
                        <a href="/uredi/urnik?predmet={{predmet.id}}">
                            {{predmet.ime}}
                        </a>
                        <small>
                            {{predmet.kratica}} /
                            {{predmet.stevilo_studentov|default:'?'}}
                        </small>
                        <a href="/uredi/predmet/{{predmet.id}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                        <a href="/uredi/pobrisi/predmet/{{predmet.id}}/">
                            <i class="tiny material-icons">delete</i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
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
                {% for ucilnica in ucilnice %}
                <tr>
                    <td>
                        <a href="/uredi/urnik?ucilnica={{ucilnica.id}}" class="{{ucilnica.vidna|yesno:',skrita'}}">
                            {{ucilnica.oznaka}}
                        </a>
                        <small>{{ucilnica.velikost|default:'?'}}</small>
                        %if ucilnica.racunalniska:
                        <i class="tiny material-icons">computer</i>
                        %end
                        <a href="/uredi/ucilnica/{{ucilnica.id}}/">
                            <i class="tiny material-icons">edit</i>
                        </a>
                        <a href="/uredi/pobrisi/ucilnica/{{ucilnica.id}}/">
                            <i class="tiny material-icons">delete</i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% else %}

<div class="container">
<div class="row">
    {% for stolpec in stolpci_smeri %}
    <div class="col s3">
        <table class="highlight">
            {% for smer in stolpec %}
            <thead>
                <tr>
                    <th>{{smer.ime}}</th>
                </tr>
            </thead>
            <tbody>
                {% for letnik in smer.letniki %}
                <tr>
                    <td style="padding: 5px">
                        <a href="/letnik/{{letnik.id}}/">{{letnik.opis}}</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
    <div class="col s2">
        <table class="highlight">
            <thead>
                <tr>
                    <th>Učilnica</th>
                </tr>
            </thead>
            <tbody>
                {% for ucilnica in ucilnice %}
                <tr>
                    <td style="padding: 5px">
                        <a href="/ucilnica/{{ucilnica.id}}/">
                            {{ucilnica.oznaka}}
                        </a>
                        <small>
                        {% if ucilnica.racunalniska %}
                        <i class="tiny material-icons">computer</i>
                        {% endif %}
                        ({{ucilnica.velikost|default:'?'}} mest)</small>
                    </td>
                </tr>
                {% endfor %}
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
                {% for oseba in osebe %}
                <tr>
                    <td style="padding: 5px">
                        <a href="/oseba/{{oseba.id}}/">
                            {{oseba.ime}} <strong>{{oseba.priimek}}</strong>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
</div>
{% endif %}

{% endblock content %}