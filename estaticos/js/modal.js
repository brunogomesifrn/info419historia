class Modal {
    constructor(id, componentes){
        const size = 'size' in componentes? 'modal-' + componentes['size'] : '',
              fechar = `
                <button type="button" class="close" data-dismiss="modal" aria-label="Fechar">
                    <span aria-hidden="true">&times;</span>
                </button>`,
              content = 'content' in componentes? componentes['content'] : (
                ('title' in componentes? `
                    <div class="modal-header">
                        <h5 class="modal-title">
                            ` + componentes['title'] + `
                        </h5>
                        ` + fechar + `
                    </div>` : '') +
                ('body' in componentes?
                    '<div class="modal-body">'+componentes['body']+'</div>' : '') +
                ('footer' in componentes?
                    '<div class="modal-footer">'+componentes['footer']+'</div>' : ''));
        this.$element = $(`
            <div class="modal fade" id="`+id+`" tabindex="-1" role="dialog" aria-labelledby="title" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered `+size+`" role="document">
                    <div class="modal-content">` +
                        content + `
                    </div>
                </div>
            </div>`);
    }
    add_to_body() {
        $('body').append(this.$element);
        if (this.$element.find('form').length) {
            this.$element.find('button[type=submit]').click((e) => {
                // $('form#'+$(e.target).attr('form')).submit();
                console.log($(e.target).parents('form').serializeArray())
            });
        }
        return this
    }
    on_open(to_do) {
        this.$element.on('show.bs.modal', to_do);
        return this
    }
    on_close(to_do) {
        this.$element.on('hide.bs.modal', to_do);
        return this
    }
    open() {
        this.$element.modal('show');
        return this
    }
}

function M(id, componentes){
    return new Modal(id, componentes)
}