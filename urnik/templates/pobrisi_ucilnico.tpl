% rebase('osnova.tpl')
<form method="post">
    Ali ste prepričani, da želite pobrisati sledečo učilnico:
    {{ucilnica['oznaka']}}
    <button class="btn waves-effect waves-light" type="submit">
        {{ 'Pobriši' }}
    </button>
</form>
