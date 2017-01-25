<!DOCTYPE html>
<html>
<head>
    <link href="http://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.8/css/materialize.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <style>
        body {
            background: #ddd;
        }
        #urnik {
            position: absolute;
            left: 5%;
            top: 5%;
            width: 90%;
            height: 90%;
            background: #fff;
        }
        #dnevi {
            position: absolute;
            left: 5%;
            top: 0%;
            width: 95%;
            height: 100%;
            color: #333;
        }
        #ure {
            position: absolute;
            left: 0%;
            top: 5%;
            width: 100%;
            height: 95%;
            color: #333;
        }
        #srecanja {
            position: absolute;
            left: 5%;
            top: 5%;
            width: 95%;
            height: 95%;
        }
        .ura {
            position: absolute;
            border-bottom: solid 1px #eee;
            width: 100%;
        }
        .ura span {
            width: 5%;
            text-align: right;
            position: relative;
            display: block;
            top: 0.75em;
            padding-right: 0.25em;
        }
        .dan {
            position: absolute;
            text-align: center;
            top: 0;
            bottom: 0;
            border-left: solid 1px #eee;
            width: 20%;
        }
        .srecanje {
            background: #eee;
            border: solid 1pt white;
            position: absolute;
            padding: 2pt;
        }
        .ucitelj, .ucilnica {
            position: absolute;
            color: #999;
            bottom: 4pt;
            font-size: 0.8em;
            z-index: 10;
        }
        .ucilnica {
            right: 4pt;
        }
        .termin {
            position: absolute;
            /*opacity: 0.6;*/
        }
        .termin:hover {
            /*opacity: 0.8;*/
        }
        .termin button {
            border-style: none;
            width: 100%;
            height: 100%;
        }
        .termin.prosto {
            background: rgba(0, 128, 0, 0.5);
        }
        .termin.alternative {
            background: rgba(255, 165, 0, 0.5);
        }
        .termin.deloma {
            background: rgba(255, 0, 0, 0.5);
        }
        .termin.deloma.alternative {
            background: repeating-linear-gradient(
              -45deg,
              rgba(255, 165, 0, 0.5),
              rgba(255, 165, 0, 0.5) 5px,
              rgba(255, 0, 0, 0.5) 5px,
              rgba(255, 0, 0, 0.5) 10px
            );
        }
        .urejanje {
            position: absolute;
            visibility: hidden;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        .srecanje:hover .urejanje {
            visibility: visible;
        }
        .podaljsevanje {
            position: absolute;
            width: 100%;
            bottom: 0;
            text-align: center;
        }
        .urejanje form {
            display: inline;
        }
        .urejanje button {
            border-style: none;
            display: inline;
            background: none;
            padding: 0;
            color: rgb(3, 155, 229);
        }
        .termin:hover .izbira_ucilnice {
            position: relative;
            visibility: visible;
            z-index: 1000000 !important;
        }
        .izbira_ucilnice {
            position: absolute;
            visibility: hidden;
        }
        .izbrana_ucilnica {
            float: left;
            width: 25%;
        }
        .izbrana_ucilnica.prosta button {
            background: green;
        }
        .izbrana_ucilnica.prosta_alternativa button {
            background: orange;
        }
        .izbrana_ucilnica.deloma_prosta button {
            background: red;
        }
    </style>
</head>

<body>
    <div class="container">
        {{!base}}
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
