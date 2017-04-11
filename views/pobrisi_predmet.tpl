% rebase('osnova.tpl')
<form method="post">
    Ali ste prepričani, da želite pobrisati sledeči predmet:
    {{predmet['ime']}}
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Pobriši' }}
    </button>
</form>
