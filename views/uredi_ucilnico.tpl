% rebase('osnova.tpl')
<form method="post">
    <div class="input-field">
        <input value="{{ucilnica['oznaka']}}" placeholder="1.01" name="oznaka" type="text" class="validate" />
        <label for="oznaka">Oznaka</label>
    </div>
    <div class="input-field">
        <input value="{{ucilnica['velikost']}}" name="velikost" type="text" class="validate" />
        <label for="velikost">Velikost</label>
    </div>
    <p>
        <input id="racunalniska" name="racunalniska" type="checkbox" {{'checked="checked"' if ucilnica['racunalniska'] else ''}} />
        <label for="racunalniska">Računalniška učilnica</label>
    </p>
    <button class="btn waves-effect waves-light" type="submit">Spremeni</button>
</form>
