% rebase('obrazec.tpl')
<h3>Urejanje letnika</h3>
<form method="post">
    <div class="input-field">
        <input value="{{letnik['smer']}}" placeholder="1Mate" name="smer" type="text" class="validate" />
        <label for="smer">Smer</label>
    </div>
    <div class="input-field">
        <input value="{{letnik['leto']}}" placeholder="3" name="leto" type="text" class="validate" />
        <label for="leto">Letnik študija</label>
    </div>
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Spremeni' if 'id' in letnik else 'Ustvari' }}
    </button>
</form>
