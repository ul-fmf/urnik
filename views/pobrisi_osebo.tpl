% rebase('osnova.tpl')
<form method="post">
    Ali ste prepričani, da želite pobrisati sledečo osebo:
    {{oseba['ime']}} {{oseba['priimek']}}
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Pobriši' }}
    </button>
</form>
