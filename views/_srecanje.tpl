% if nacin == 'urejanje':
    % left = (srecanje['dan'] - 1 + srecanje['zamik']) * enota_sirine
    % top = (srecanje['ura'] - min_ura) * enota_visine
    % height = srecanje['trajanje'] * enota_visine
    % width = srecanje['sirina'] * enota_sirine
    % style = 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
    <div class="srecanje" style="{{ style }};">
        <div class="predmet">
            {{srecanje['predmet']['ime']}} {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </div>
        <div class="ucitelj">
            <a href="/uredi/urnik?oseba={{srecanje['ucitelj']['id']}}">
                {{srecanje['ucitelj']['priimek']}}
            </a>
        </div>
        <div class="ucilnica">
            <a href="/uredi/urnik?ucilnica={{srecanje['ucilnica']['id']}}">
                {{srecanje['ucilnica']['oznaka']}}
            </a>
        </div>
        <div class="urejanje">
            % if srecanje['trajanje'] > 1:
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/trajanje/">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] - 1}}">
                <button>
                    <i class="tiny material-icons">file_upload</i> skrajšaj
                </button>
            </form>
            % end
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/trajanje/">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] + 1}}">
                <button>
                    <i class="tiny material-icons">file_download</i> podaljšaj
                </button>
            </form>
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/izbrisi/">
                <button>
                    <i class="tiny material-icons">delete</i> pobriši
                </button>
            </form>
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/podvoji/">
                <button>
                    <i class="tiny material-icons">content_copy</i> podvoji
                </button>
            </form>
            <a href="/uredi/srecanje/{{srecanje['id']}}/premakni/">
                <i class="tiny material-icons">open_with</i> premakni
            </a>
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/odlozi/">
                <button>
                    <i class="tiny material-icons">move_to_inbox</i> odloži
                </button>
            </form>
            <a href="/uredi/srecanje/{{srecanje['id']}}/">
                <i class="tiny material-icons">edit</i> uredi
            </a>
        </div>
    </div>
% elif nacin == 'odlozisce':

    <div class="srecanje">
        <div class="predmet">
            {{srecanje['predmet']['ime']}} {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </div>
        <div class="ucitelj">
            <a href="/uredi/urnik?oseba={{srecanje['ucitelj']['id']}}">
                {{srecanje['ucitelj']['priimek']}}
            </a>
        </div>
        <div class="ucilnica">
            <a href="/uredi/urnik?ucilnica={{srecanje['ucilnica']['id']}}">
                {{srecanje['ucilnica']['oznaka']}}
            </a>
        </div>
        <div class="urejanje">
            % if srecanje['trajanje'] > 1:
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/trajanje/">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] - 1}}">
                <button>
                    <i class="tiny material-icons">file_upload</i> skrajšaj
                </button>
            </form>
            % end
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/trajanje/">
                <input type="hidden" name="next" value="{{next}}">
                <input type="hidden" name="trajanje" value="{{srecanje['trajanje'] + 1}}">
                <button>
                    <i class="tiny material-icons">file_download</i> podaljšaj
                </button>
            </form>
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/izbrisi/">
                <button>
                    <i class="tiny material-icons">delete</i> pobriši
                </button>
            </form>
            <form method="post" action="/uredi/srecanje/{{srecanje['id']}}/podvoji/">
                <button>
                    <i class="tiny material-icons">content_copy</i> podvoji
                </button>
            </form>
            <a href="/uredi/srecanje/{{srecanje['id']}}/premakni/">
                <i class="tiny material-icons">open_with</i> premakni
            </a>
            <a href="/uredi/srecanje/{{srecanje['id']}}/">
                <i class="tiny material-icons">edit</i>
            </a>
        </div>
    </div>

% elif nacin == 'ogled':
% left = (srecanje['dan'] - 1 + srecanje['zamik']) * enota_sirine
% top = (srecanje['ura'] - min_ura) * enota_visine
% height = srecanje['trajanje'] * enota_visine
% width = srecanje['sirina'] * enota_sirine
% style = 'left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
<div class="srecanje" style="{{ style }};">
    <div class="predmet">
        <a href="/predmet/{{srecanje['predmet']['id']}}/">{{srecanje['predmet']['ime'] if (srecanje['sirina'] >= 0.5 and len(srecanje['predmet']['ime']) < 45 and srecanje['trajanje'] > 1) or srecanje['sirina'] == 1 else srecanje['predmet']['kratica']}}</a>
        <span class="tip">
             {{srecanje['tip']}}{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}
        </span>
    </div>
    <div class="ucitelj">
        <a href="/oseba/{{srecanje['ucitelj']['id']}}/">{{srecanje['ucitelj']['priimek']}}</a>
    </div>
    % if srecanje['sirina'] >= 0.5:
    <div class="ucilnica">
        <a href="/ucilnica/{{srecanje['ucilnica']['id']}}/">{{srecanje['ucilnica']['oznaka']}}</a>
    </div>
    % end
</div>
% end