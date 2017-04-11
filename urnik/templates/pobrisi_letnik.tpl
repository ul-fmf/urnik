% rebase('osnova.tpl')
<form method="post">
    Ali ste prepričani, da želite pobrisati sledeči letnik in ga odjaviti iz vseh njegovih srečanj:
    {{letnik['smer']}}, {{letnik['leto']}}. letnik
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Pobriši' }}
    </button>
</form>
