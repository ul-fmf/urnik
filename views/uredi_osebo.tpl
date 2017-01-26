% rebase('obrazec.tpl')
% urejanje = defined('oseba')
% oseba = get('oseba', {'ime': '', 'priimek': '', 'email': ''})
<h3>Urejanje osebe</h3>
<form method="post">
    <div class="input-field">
        <input value="{{oseba['ime']}}" placeholder="Janez" name="ime" type="text" class="validate">
        <label for="ime">Ime</label>
    </div>
    <div class="input-field">
        <input value="{{oseba['priimek']}}" placeholder="Novak" name="priimek" type="text" class="validate">
        <label for="priimek">Priimek</label>
    </div>
    <div class="input-field">
        <input value="{{oseba['email'] or ''}}" placeholder="janez.novak@fmf.uni-lj.si" name="email" type="text" class="validate">
        <label for="email">Elektronska pošta</label>
    </div>
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Spremeni' if urejanje else 'Ustvari' }}
    </button>
</form>
