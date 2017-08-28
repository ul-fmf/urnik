{% load static %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link href="http://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.8/css/materialize.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Urnik OM FMF {{ naslov|yesno:'- ' }}{{ naslov }} – poletni semester 2016/17</title>
    <link rel="stylesheet" href="{% static 'stil.css' %}">
</head>

<body>
    <div class="navbar-fixed">
  <nav>
    <div class="nav-wrapper">
      <span class="brand-logo center">
        <i class="large material-icons">schedule</i>
        {{ naslov|default:'Urnik' }}
      </span>
      <ul>
        <li id="domov"><a href="{{ domov|default:'/' }}"><i class="material-icons left">home</i>Urnik OM FMF – poletni semester 2016/17</a></li>
      </ul>
    </div>
  </nav>

    </div>
    <div class="container" style="position: absolute; width: 100%; bottom: 0; top: 64px">
        {% block content %}{% endblock content %}
    </div>

    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.8/js/materialize.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $('select').material_select();
        });
    </script>
</body>
</html>
