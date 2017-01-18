% rebase('osnova.tpl')
% urejanje = defined('letnik')
% letnik = get('letnik', {'smer': '', 'leto': '', 'stevilo_studentov': ''})
<form method="post">
    <div class="input-field">
        <input value="{{letnik['smer']}}" placeholder="1Mate" name="smer" type="text" class="validate" />
        <label for="smer">Smer</label>
    </div>
    <div class="input-field">
        <input value="{{letnik['leto']}}" placeholder="3" name="leto" type="text" class="validate" />
        <label for="leto">Letnik študija</label>
    </div>
    <div class="input-field">
        <input value="{{letnik['stevilo_studentov']}}" name="stevilo_studentov" type="text" class="validate" />
        <label for="stevilo_studentov">Število študentov</label>
    </div>
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Spremeni' if urejanje else 'Ustvari' }}
    </button>
</form>
