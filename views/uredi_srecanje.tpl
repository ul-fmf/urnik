% rebase('obrazec.tpl')
<form method="post">
    <div class="input-field">
        <select name="predmet">
            <option value="" {{ '' if srecanje['predmet'] else 'selected' }}>brez učilnice</option>
            % for predmet in predmeti:
            <option value="{{predmet['id']}}" {{ 'selected' if predmet['id'] == srecanje['predmet'] else '' }}>{{predmet['opis']}}</option>
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
        <select name="ucitelj">
            <option value="" {{ '' if srecanje['ucitelj'] else 'selected' }}>brez učitelja</option>
            % for ucitelj in ucitelji.values():
            <option value="{{ucitelj['id']}}" {{ 'selected' if ucitelj['id'] == srecanje['ucitelj'] else '' }}>{{ucitelj['priimek']}} {{ucitelj['ime']}}</option>
            % end
        </select>
        <label>Učitelj</label>
    </div>
    <input type="hidden" name="next" value="{{next}}">
    <button class="btn waves-effect waves-light" type="submit">
        Spremeni
    </button>
</form>
