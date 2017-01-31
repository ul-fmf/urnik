% rebase('obrazec.tpl')
<h3>Urejanje srečanja</h3>
<form method="post">
    <div class="input-field">
        <select name="predmet">
            <option value="" {{ '' if srecanje['predmet'] else 'selected' }}>brez predmeta</option>
            % for predmet in predmeti.values():
            <option value="{{predmet['id']}}" {{ 'selected' if predmet['id'] == srecanje['predmet']['id'] else '' }}>{{predmet['ime']}} {{'({})'.format(predmet['opis_letnikov']) if predmet['opis_letnikov'] else ''}}</option>
            % end
        </select>
        <label>Predmet</label>
    </div>
    <div class="input-field">
        <select name="tip">
            % for tip, opis in (('P', 'predavanja'), ('S', 'seminar'), ('V', 'vaje'), ('L', 'laboratorijske vaje')):
            <option value="{{tip}}" {{ 'selected' if tip == srecanje['tip'] else '' }}>{{opis}}</option>
            % end
        </select>
        <label>Tip</label>
    </div>
    <div class="input-field">
        <input value="{{srecanje['oznaka'] if srecanje['oznaka'] else ''}}" placeholder="1" name="oznaka" type="text" class="validate" />
        <label for="oznaka">Oznaka skupine</label>
    </div>
    <div class="input-field">
        <select name="ucitelj">
            <option value="" {{ '' if srecanje['ucitelj'] else 'selected' }}>brez učitelja</option>
            % for ucitelj in ucitelji.values():
            <option value="{{ucitelj['id']}}" {{ 'selected' if ucitelj['id'] == srecanje['ucitelj']['id'] else '' }}>{{ucitelj['priimek']}} {{ucitelj['ime']}}</option>
            % end
        </select>
        <label>Učitelj</label>
    </div>
    <div class="input-field">
        <select name="ucilnica">
            <option value="" {{ '' if srecanje['ucilnica'] else 'selected' }}>brez učilnice</option>
            % for ucilnica in ucilnice.values():
            <option value="{{ucilnica['id']}}" {{ 'selected' if ucilnica['id'] == srecanje['ucilnica']['id'] else '' }}>{{ucilnica['oznaka']}} ({{ucilnica['velikost']}})</option>
            % end
        </select>
        <label>Učitelj</label>
    </div>
    <input type="hidden" name="next" value="{{next}}">
    <button class="btn waves-effect waves-light" type="submit">
        Spremeni
    </button>
</form>
