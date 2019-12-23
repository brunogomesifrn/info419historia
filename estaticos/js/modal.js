class Modal {
    static autocreated = {}

    constructor(id, componentes={}) {
        if (!id)
            return;

        this.title = 'title' in componentes? componentes['title'] : null;
        this.body = 'body' in componentes? componentes['body'] : null;
        this.footer = 'footer' in componentes? componentes['footer'] : null;
        this.size = 'size' in componentes? 'modal-' + componentes['size'] : '';

        const modal = this
        $("button[data-toggle='modal'][data-target='#"+id+"']").click(function(e) {
            modal.open(e);
        });

        this.on_open = function(){}
        this.on_close = function(){}
    }

    static get element() {
        return $('div.modal.auto-created');
    }

    static autocreate() {
        const pop = function(array, key){
            const value = array[key];
            delete array[key];
            return value;
        };
        $('button.autocreate').each((i, el) => {
            const $button = $(el);
            var data = $button.data();
            const modal = Modal.SUB_CLASSES[pop(data, 'modal')],
                  id = pop(data, 'target').substr(1);
            delete data.toggle;

            var componentes = {}
            for (const componente of ['title', 'body', 'footer', 'size']) {
                if (componente in data)
                    componentes[componente] = pop(data, componente);
            }
            data = Object.values(data);
            data.reverse();
            data.unshift(id);
            data.push(componentes);

            Modal.autocreated[id] = new modal(...data);
        });
        console.log(Modal.autocreated)
    }

    create() {
        const $modal = Modal.element;

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
    }

    destruct() {
        const $modal = Modal.element;
        $modal.find('.modal-title').html('').show();
        $modal.find('.modal-body').html('').show();
        $modal.find('.modal-footer').html('').show();
        $modal.find('.modal-dialog').removeClass(this.size);
    }

    open(event) {
        this.create()
        const modal = this,
              $modal = Modal.element;
        $modal.on('hidden.bs.modal', (e) => {
            modal.close(e);
        });
        $modal.modal('show');
        this.on_open(event);
        this.open_event = event;
        return this;
    }

    close(event) {
        this.destruct()
        this.on_close(event, this.open_event);
        return this;
    }
}


class ModalAjax extends Modal {
    constructor(id, url, componentes){
        super(id, {
            title: 'title' in componentes? componentes['title'] : null,
            body: 'Carregando...',
            footer: 'footer' in componentes? componentes['footer'] : null,
            size: 'size' in componentes? componentes['size'] : ''
        })
        this.url = url
        this.on_get = () => {}
    }

    get_data(options, done, fail) {
        const $modal = Modal.element;

        if (!fail)
            fail = function(xhr, status, error) {
                $modal.find('.modal-body').html("Algo deu errado (" + xhr.status + ")... Tente novamente mais tarde.");
            }
        if (!options || !done)
            fail()
        
        const request = $.ajax(options);
        request.done(function(result, status, xhr) {
            done.call(this, result, status, xhr);
            this.on_get(Modal.element);
        });
        request.fail(fail);
    }
}


class ModalPage extends ModalAjax {
    constructor(id, url, componentes){
        super(id, url, componentes)
    }

    get_data(){
        super.get_data(
            {
                type: 'GET',
                context: this,
                url: this.url,
                dataType: 'html'
            },
            function(page) {
                Modal.element.find('.modal-body').html(page);
            }
        );
    }

    create(){
        super.create();
        this.get_data();
    }
}


class ModalForm extends ModalAjax {
    constructor(id, title, url, csrf_token){
        super(id, url, {
            title: title,
            footer: `<input type=hidden name="acao" value="" />
                     <button type="submit" class="btn btn-primary">Salvar</button>`,
            size: 'lg',
        });
        this.csrf_token = csrf_token
        this.on_save = () => {}
    }

    get_data() {
        super.get_data(
            {
                type: 'POST',
                context: this,
                url: this.url,
                data: new FormData(Modal.element.find('form')[0]),
                processData: false,
                contentType: false,
                dataType: 'text'
            },
            function(data_str) {
                try {
                    const data = $.parseJSON(data_str);
                    this.on_save(data.id, this.open_event)
                } catch (e) {
                    console.log(e);
                    const $modal = Modal.element;
                    $modal.find('.modal-body').html(data_str);
                    $modal.find('button[type="submit"]')
                        .text('Salvar')
                        .prop('disabled', false);
                }
            }
        )
    }

    create() {
        super.create()
        const $modal = Modal.element;

        var $csrf_token = $modal.find("[name='csrfmiddlewaretoken']");
        if (!$csrf_token.length)
            $csrf_token = $("<input type='hidden' name='csrfmiddlewaretoken' value='"+this.csrf_token+"' />");

        $modal.find('.modal-content')
            .wrapInner('<form method="post" class="text-center" enctype="multipart/form-data"></form>')
            .find('form').append($csrf_token);

        this.get_data()
        $modal.find('button[type="submit"]').click((e) => {
            $(e.target).text('Salvando...').prop('disabled', true).prev().val('salvar')
            this.get_data()
            return false;
        });

    }

    destruct() {
        super.destruct()
        Modal.element.find('form').contents().unwrap()
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


function MP(id, url, componentes){
    return new ModalPage(id, url, componentes)
}


function MF(id, title, url, csrf_token){
    return new ModalForm(id, title, url, csrf_token);
}


function MD(id, nome, url){
    return new ModalDeletion(id, nome, url);
}

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
        </div>
    `))
    Modal.SUB_CLASSES = {
        'Ajax': ModalAjax,
        'Page': ModalPage,
        'Deletion': ModalDeletion,
        'Form': ModalForm
    }
    Modal.autocreate()
});
