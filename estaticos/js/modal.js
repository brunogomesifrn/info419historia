$(() => {
    $('body').append($(`
        <div class="modal fade auto-created" tabindex="-1" role="dialog" aria-labelledby="title" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"></h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Fechar">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body"></div>
                    <div class="modal-footer"></div>
                </div>
            </div>
        </div>`))
});

class Modal {
    constructor(id, componentes) {
        if (!id)
            return;

        this.show_form = 'show_form' in componentes? componentes['show_form'] : false;
        this.title = 'title' in componentes? componentes['title'] : null;
        this.body = 'body' in componentes? componentes['body'] : null;
        this.footer = 'footer' in componentes? componentes['footer'] : null;
        this.size = 'size' in componentes? 'modal-' + componentes['size'] : '';

        const modal = this
        $("button[data-toggle='modal'][data-target='#"+id+"']").click((e) => {
            modal.open($(e.target));
        });

        this.on_open = function(){}
        this.on_close = function(){}
    }
    open($button) {
        const modal = this,
              $modal = $('div.modal.auto-created');
        if (this.show_form)
            $modal.find('.modal-content')
                .wrapInner('<form method="post" class="text-center"></form>');

        $modal.on('hidden.bs.modal', (e) => {
            modal.close(e);
        });

        const $title = $modal.find('.modal-title'),
              $body = $modal.find('.modal-body'),
              $footer = $modal.find('.modal-footer'),
              $dialog = $modal.find('.modal-dialog');

        if (this.title)
            $title.html(this.title);
        else
            $title.hide();

        if (this.body)
            $body.html(this.body);
        else
            $body.hide();

        if (this.footer)
            $footer.html(this.footer);
        else
            $footer.hide();

        $dialog.addClass(this.size);
        $modal.modal('show');
        this.on_open($modal, $button);
        return this;
    }
    close(e) {
        const $modal = $('div.modal.auto-created'),
              $form = $modal.find('form');
        if ($form.length)
            $form.contents().unwrap();
        $modal.find('.modal-title').html('').show();
        $modal.find('.modal-body').html('').show();
        $modal.find('.modal-footer').html('').show();
        $modal.find('.modal-dialog').removeClass(this.size);
        this.on_close(e);
        return this;
    }
}

class ModalForm extends Modal {
    constructor(id, title, form, csrf_token){
        super(id, {
            title: title,
            body: "<input type='hidden' name='csrfmiddlewaretoken' value='"+csrf_token+"' />" + form,
            footer: '<button type="submit" class="btn btn-primary" name="acao" value="'+id+'">Salvar</button>',
            size: 'lg',
            show_form: true
        });
    }
}

class ModalDeletion extends Modal {
    static create_from_buttons(){
        var modals = []
        $('button[data-modal-role=delete').each((i, el) => {
            const $button = $(el);
            modals.push(MD($button.data('target').substr(1),
                           $button.data('nome'),
                           $button.data('url')))
        });
        return modals;
    }

    constructor(id, nome, url){
        super(id, {
            title: "Deseja realmente apagar " + nome + "?",
            footer: `<button type="button" class="btn btn-success" data-dismiss="modal">Cancelar</button>
                     <a href="`+url+`"><button type="button" class="btn btn-danger">Apagar</button></a>`
        });
    }
}

function M(id, componentes){
    return new Modal(id, componentes);
}

function MF(id, title, form, csrf_token){
    return new ModalForm(id, title, form, csrf_token);
}

function MD(id, nome, url){
    return new ModalDeletion(id, nome, url);
}