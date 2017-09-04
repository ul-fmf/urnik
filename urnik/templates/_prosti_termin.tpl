% min_ura, max_ura = 7, 20
% enota_visine = 1 / (max_ura - min_ura)
% dnevi = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek')
% enota_sirine = 1 / len(dnevi)
% left = (dan - 1) * enota_sirine
% top = (ura - min_ura) * enota_visine
% height = enota_visine
% width = enota_sirine
% style = 'position: absolute; left: {:.2%}; width: {:.2%}; top: {:.2%}; height: {:.2%}'.format(left, width, top, height)
<div class="termin {{termin['zasedenost']}}" style="{{style}}">
    <div class="izbira_ucilnice">
    % for ucilnica in termin['ucilnice']:
        <form method="post" class="izbrana_ucilnica {{ucilnica.zasedenost}} {{ucilnica.ustreznost}}">
            <input type="hidden" name="next" value="{{next}}">
            <input value="{{dan}}" name="dan" type="hidden">
            <input value="{{ura}}" name="ura" type="hidden">
            <input value="{{ucilnica.id}}" name="ucilnica" type="hidden">
            <button class="">{{ucilnica.oznaka}}<br><small>{{ucilnica.velikost}}</small></button>
        </form>
    % end
    </div>
</div>
