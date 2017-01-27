% rebase('obrazec.tpl')
% urejanje = defined('predmet')
% predmet = get('predmet', {'ime': '', 'kratica': '', 'stevilo_studentov': None, 'racunalniski': False, 'letniki': []})
<h3>Urejanje predmeta</h3>
<form method="post">
    <div class="input-field">
        <input value="{{predmet['ime']}}" placeholder="Podatkovne baze 1" name="ime" type="text" class="validate" />
        <label for="ime">Ime</label>
    </div>
    <div class="input-field">
        <input value="{{predmet['kratica']}}" placeholder="PB 1" name="kratica" type="text" class="validate" />
        <label for="kratica">Kratica</label>
    </div>
    <div class="input-field">
        <input value="{{'' if predmet['stevilo_studentov'] is None else predmet['stevilo_studentov']}}" placeholder="neznano" name="stevilo_studentov" type="text" class="validate" />
        <label for="stevilo_studentov">Število študentov</label>
    </div>
    <p>
        <input id="racunalniski" name="racunalniski" type="checkbox" {{'checked="checked"' if predmet['racunalniski'] else ''}} />
        <label for="racunalniski">Vaje potekajo v računalniški učilnici</label>
    </p>
    <div class="input-field">
        <select multiple name="letniki">
            % for letnik in letniki.values():
            <option value="{{letnik['id']}}" {{ 'selected' if letnik['id'] in predmet['letniki'] else '' }}>{{letnik['smer']}}, {{letnik['leto']}}</option>
            % end
        </select>
        <label>Letniki</label>
    </div>
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Spremeni' if urejanje else 'Ustvari' }}
    </button>
</form>
