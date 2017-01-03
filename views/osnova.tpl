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
            left: 10%;
            top: 0%;
            width: 90%;
            height: 100%;
        }
        #ure {
            position: absolute;
            left: 0%;
            top: 10%;
            width: 100%;
            height: 90%;
        }
        #srecanja {
            position: absolute;
            left: 10%;
            top: 10%;
            width: 90%;
            height: 90%;
        }
        .ura {
            position: absolute;
            border-bottom: solid 1px #eee;
            width: 100%;
            padding-left: 5em;
        }
        .dan {
            position: absolute;
            text-align: center;
            top: 0;
            bottom: 0;
            border-left: solid 1px #eee;
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
        }
        .ucilnica {
            right: 4pt;
        }
    </style>
</head>

<body>
    <div class="container">
        {{!base}}
    </div>

    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.8/js/materialize.min.js"></script>
</body>
</html>
