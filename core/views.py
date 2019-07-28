from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# from .forms import (UsuarioForm, TurmaForm, AtividadeForm, GrupoForm,
#                     TipoForm, DocumentoForm, QuestaoForm, AlternativaForm)
from .forms import (UsuarioCriacaoForm, UsuarioEdicaoForm, TurmaForm,
                    AtividadeForm, TipoForm, DocumentoForm, QuestaoForm,
                    AlternativaForm)
# from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa
from .models import Usuario, Turma, Atividade, Documento, Questao, Alternativa
from django.http import HttpResponse


# Create your views here.


@login_required
def perfil(request):
    turmas = Turma.objects.order_by('nome')
    atividades = Atividade.objects.order_by('fim')
    contexto = {
        'turmas': turmas,
        'atividades': atividades,
    }
    return render(request, 'registration/perfil.html', contexto)

# @login_required
# def turmas(request):
#     turmas = Turma.objects.order_by('nome')
#     contexto = {
#         'turmas': turmas,
#     }
#     return render(request, 'turmas.html', contexto)


@login_required
def usuarios(request):
    usuarios = Usuario.objects.order_by('nome')
    contexto = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios.html', contexto)


def registro(request):
    form = UsuarioCriacaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    contexto = {
        'form': form,
        'titulo': 'Cadastre-se',
    }
    return render(request, 'registration/registro.html', contexto)


@login_required
def usuario_edicao(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    form = UsuarioEdicaoForm(request.POST or None, instance=usuario)
    # user_form = UserCreationForm(request.POST or None, instance=usuario.user)
    # if form.is_valid() and user_form.is_valid():
    if form.is_valid():
        # user = user_form.save()
        # usuario = form.save(commit=False)
        # usuario.user = user
        # usuario.save()
        form.save()
        return redirect('usuarios')
    contexto = {
        'form': form,
        # 'user_form': user_form,
        'titulo': 'Editar %s' % usuario,
    }
    return render(request, 'registration/registro.html', contexto)


@login_required
def usuario_remocao(request, id):
    usuario = get_object_or_404(User, pk=id)
    usuario.delete()
    return render(request, 'usuarios.html')


@login_required
def turma(request, id):
    turma = get_object_or_404(Turma, pk=id)
    contexto = {
        'turma': turma,
    }
    return render(request, 'turma.html', contexto)


@login_required
def turma_cadastro(request):
    form = TurmaForm(request.POST or None)
    acao = ""
    if form.is_valid():
        form.save()
        form = TurmaForm()
        acao = 'fechar'
    contexto = {
        'form': form,
        'acao': acao,
        'titulo': 'Cadastrar uma nova turma',
    }
    return render(request, 'turma_cadastro.html', contexto)


@login_required
def turma_edicao(request, id):
    turma = get_object_or_404(Turma, pk=id)
    form = TurmaForm(request.POST or None, instance=turma)
    if form.is_valid():
        form.save()
        return redirect('turma', id)
    contexto = {
        'form': form,
        'titulo': 'Editar turma',
    }
    return render(request, 'turma_cadastro.html', contexto)


@login_required
def turma_remocao(request, id):
    turma = get_object_or_404(Turma, pk=id)
    turma.delete()
    return redirect('perfil')


def atividade_formulario(request,
                         titulo,
                         default_quant_questoes=1,
                         default_quant_alternativas=None,
                         atividade=None):
    acao = request.POST['acao'] if 'acao' in request.POST else ''

    atividade_form = AtividadeForm(request.POST or None,
                                   use_required_attribute=False,
                                   instance=atividade)

    # A quantidade de questões, inicialmente, é um, mas pode mudar
    # de acordo com o valor recebido pelo formulário e se a ação for
    # nova questão ou remover
    quant_questoes = default_quant_questoes
    if 'quant_questoes' in request.POST:
        quant_questoes = int(request.POST['quant_questoes'])
    if acao == "nova_questao":
        quant_questoes += 1
    elif acao == "remover_questao":
        quant_questoes -= 1

    # A quantidade de alternativas é uma lista porque podem existir diversas
    # questões na mesma página. O índice 0 corresponde à questão 1, o 1 à 2
    # etc. Todas as questões começam com 2 alternativas, mas podem mudar pelo
    # valor recebido ou pela ação.
    quant_alternativas = (default_quant_alternativas +
                          [2] *
                          (quant_questoes - len(default_quant_alternativas))
                          if (default_quant_alternativas)
                          else ([2] * quant_questoes))

    # O laço vai de 1 à quantidade de questões
    for questao in range(1, quant_questoes + 1):
        if 'quant_alternativas-q%d' % questao in request.POST:
            quant_alternativas[questao - 1] = (
                int(request.POST['quant_alternativas-q%d' % questao])
            )
        if acao == "nova_alternativa-q%d" % questao:
            quant_alternativas[questao - 1] += 1
        elif acao == "remover_alternativa-q%d" % questao:
            quant_alternativas[questao - 1] -= 1

    # Como existem diversas questões e alternativas, também serão necessários
    # diversos formulários, armazenados em listas.
    questoes_forms = []

    # O índice 0 dessa lista irá armazenar uma outra lista com os formulários
    # das alternativas da questão 1, o 1 uma com os da questão 2 etc.
    alternativas_forms_questao = []
    for n in range(1, quant_questoes + 1):
        try:
            questao = atividade.questao_set.all()[n - 1]
        except (IndexError, AttributeError):
            questao = None
        # É armazemado um formulário para cada questão, todos dentro da lista
        # "questoes_forms". O parâmetro "prefix" serve pata nomear cada
        # formulário e evitar que os dados sejam misturados. As questões são
        # nomeadas "questao1", "questao2", ...
        questoes_forms.append(QuestaoForm(request.POST or None,
                                          prefix="questao%d" % n,
                                          use_required_attribute=False,
                                          instance=questao))
        # Essa lista armazenará somente os formulários as alternativas da mesma
        # questão
        alternativas_forms = []
        # O laço vai de 1 a quantidade de alternativas da questão n
        for m in range(1, quant_alternativas[n - 1] + 1):
            try:
                alternativa = questao.alternativa_set.all()[m - 1]
            except (IndexError, AttributeError):
                alternativa = None
            # Arzenados os formulários das alternativas com o prefix
            # "alternativa1-q1", "alternativa2-q1", ...,
            # "alternativa1-q2", "alternativa2-q2", ...
            alternativas_forms.append(AlternativaForm(
                request.POST or None,
                prefix="alternativa%d-q%d" % (m, n),
                use_required_attribute=False,
                instance=alternativa))
        # Armazenada as listas na outra
        alternativas_forms_questao.append(alternativas_forms)

    if acao == 'salvar':
        valido = (atividade_form.is_valid() and
                  all([questao_form.is_valid()
                       for questao_form in questoes_forms]) and
                  all([alternativa_form.is_valid()
                       for alternativa_form in alternativas_forms
                       for alternativas_forms in alternativas_forms_questao]))
    else:
        valido = False
    if valido:
        atividade = atividade_form.save()
        for questao_form, alternativas_forms in zip(
                questoes_forms,
                alternativas_forms_questao):
            questao = questao_form.save(commit=False)
            questao.atividade = atividade
            questao.save()
            questao.documentos.clear()
            for documento in questao_form.cleaned_data['documentos']:
                questao.documentos.add(documento)

            for alternativa_form in alternativas_forms:
                alternativa = alternativa_form.save(commit=False)
                alternativa.questao = questao
                alternativa.save()
        return redirect('atividade', atividade.id)
    contexto = {
        'atividade_form': atividade_form,
        'questoes_forms': questoes_forms,
        'alternativas_forms_questao': alternativas_forms_questao,
        'titulo': titulo,
    }
    return render(request, 'atividade_cadastro.html', contexto)


@login_required
def atividade_cadastro(request):
    return atividade_formulario(request, 'Cadastrar uma nova atividade')


@login_required
def atividade(request, id):
    atividade = get_object_or_404(Atividade, pk=id)
    questoes = atividade.questao_set.all()
    contexto = {
        'atividade': atividade,
        'questoes': questoes,
    }
    return render(request, 'atividade.html', contexto)


@login_required
def atividade_edicao(request, id):
    atividade = get_object_or_404(Atividade, pk=id)

    quant_questoes = atividade.questao_set.count()
    quant_alternativas = [questao.alternativa_set.count()
                          for questao in atividade.questao_set.all()]

    return atividade_formulario(request,
                                'Editar atividade',
                                atividade=atividade,
                                default_quant_questoes=quant_questoes,
                                default_quant_alternativas=quant_alternativas)


@login_required
def atividade_remocao(request, id):
    atividade = get_object_or_404(Atividade, pk=id)
    atividade.delete()
    return redirect('perfil')
#
#
# @login_required
# def grupos(request, atividade_id):
#     atividade = get_object_or_404(Atividade, pk=atividade_id)
#     grupos = Grupo.objects.filter(atividade=atividade_id)
#     contexto = {
#         'grupos': grupos,
#         'atividade': atividade,
#     }
#     return render(request, 'grupos.html', contexto)
#
#
# @login_required
# def grupo_cadastro(request, atividade_id):
#     atividade = get_object_or_404(Atividade, pk=atividade_id)
#     form = GrupoForm(request.POST or None)
#     if form.is_valid():
#         grupo = form.save(commit=False)
#         grupo.atividade = atividade
#         grupo.save()
#         for item in form.data['membros']:
#             grupo.membros.add(item)
#         return redirect('grupos', atividade_id)
#     contexto = {
#         'form': form,
#         'atividade': atividade,
#     }
#     return render(request, 'grupo_cadastro.html', contexto)


@login_required
def documentos(request):
    documentos = Documento.objects.all()
    contexto = {
        'documentos': documentos,
    }
    return render(request, 'documentos.html', contexto)


@login_required
def documento_cadastro(request):
    if 'composicao' in request.POST:
        composicao = request.POST['composicao']
        if composicao == 0:
            request.POST['arquivo'] = None
        elif composicao == 1:
            request.POST['texto'] = None
    form = DocumentoForm(request.POST or None,
                         request.FILES or None, use_required_attribute=False)
    tipo_form = TipoForm(request.POST or None, use_required_attribute=False)
    if tipo_form.is_valid():
        tipo = tipo_form.save()
        data = form.data.copy()
        data['tipo'] = tipo.id
        form = DocumentoForm(data)
    if form.is_valid():
        form.save()
        return render(request, 'documento_cadastro.html', {'acao': 'fechar'})
    contexto = {
        'form': form,
        'tipo_form': tipo_form,
    }
    return render(request, 'documento_cadastro.html', contexto)
