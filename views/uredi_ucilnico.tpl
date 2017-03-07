% rebase('obrazec.tpl')
<h3>Urejanje učilnice</h3>
<form method="post">
    <div class="input-field">
        <input value="{{ucilnica['oznaka']}}" placeholder="1.01" name="oznaka" type="text" class="validate" />
        <label for="oznaka">Oznaka</label>
    </div>
    <div class="input-field">
        <input value="{{ucilnica['velikost'] if ucilnica['velikost'] else ''}}" name="velikost" type="text" class="validate" />
        <label for="velikost">Velikost</label>
    </div>
    <p>
        <input id="racunalniska" name="racunalniska" type="checkbox" {{'checked="checked"' if ucilnica['racunalniska'] else ''}} />
        <label for="racunalniska">Računalniška učilnica</label>
    </p>
    <p>
        <input id="skrita" name="skrita" type="checkbox" {{'checked="checked"' if ucilnica['skrita'] else ''}} />
        <label for="skrita">Skrita učilnica</label>
    </p>
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Spremeni' if 'id' in ucilnica else 'Ustvari' }}
    </button>
</form>
