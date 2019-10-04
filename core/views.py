from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Sum
from django.utils import timezone
from django.middleware.csrf import get_token
from .forms import *
from .models import (Usuario, Turma, Atividade, Grupo,
                     Documento, Resposta)

agora = timezone.now()


@login_required
def perfil(request, turma_id=None):
    turmas = Turma.objects.filter(membros=request.user).order_by('nome')
    atividades = Atividade.objects.order_by('fim')
    if not request.user.is_professor():
        atividades = atividades.filter(inicio__lte=agora)

    acao = request.POST.get('acao', '')
    turma_form = (turma_cadastro(request)
                  if acao == 'turma-salvar'
                  else turma_edicao(request, turma_id)
                  if turma_id
                  else TurmaForm())

    contexto = {
        'turma_form': turma_form,
        'turmas': turmas,
        'atividades': atividades,
        'agora': agora
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
@permission_required('core.view_usuario', raise_exception=True)
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
    atual = request.user
    if not atual.has_perm('core.change_usuario') and usuario != atual:
        raise PermissionDenied
    if 'permissoes' in request.POST:
        if not atual.has_perm('auth.change_permission'):
            raise PermissionDenied
        if request.POST['permissoes'] == '1':
            usuario.groups.set([Group.objects.get(name__startswith="P")])
        else:
            usuario.groups.set([Group.objects.get(name__startswith="A")])
        return redirect('usuarios')
    form = UsuarioEdicaoForm(request.POST or None, instance=usuario)
    if form.is_valid():
        form.save()
        return redirect('usuarios')
    contexto = {
        'form': form,
        'titulo': 'Editar %s' % usuario,
        'usuario': usuario,
    }
    return render(request, 'registration/registro.html', contexto)


@login_required
@permission_required('core.delete_usuario', raise_exception=True)
def usuario_remocao(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    usuario.delete()
    return render(request, 'usuarios.html')


@login_required
@permission_required('core.view_turma', raise_exception=True)
def turma(request, id):
    turma = get_object_or_404(Turma, pk=id)
    contexto = {
        'turma': turma,
    }
    return render(request, 'turma.html', contexto)


@login_required
@permission_required('core.add_turma', raise_exception=True)
def turma_cadastro(request):
    form = TurmaForm(request.POST)
    if form.is_valid():
        form.save()
        form.data = {}
    return form


@login_required
@permission_required('core.change_turma', raise_exception=True)
def turma_edicao(request, id):
    turma = get_object_or_404(Turma, pk=id)
    form = TurmaForm(request.POST or None, instance=turma)
    if form.is_valid():
        form.save()
        return redirect('turma', id)
    contexto = {
        'form': form,
        'titulo': 'Editar turma %s' % turma,
    }
    return render(request, 'turma_cadastro.html', contexto)


@login_required
@permission_required('core.delete_turma', raise_exception=True)
def turma_remocao(request, id):
    turma = get_object_or_404(Turma, pk=id)
    turma.delete()
    return redirect('perfil')


def atividade_formulario(request,
                         titulo,
                         default_quant_questoes=1,
                         default_quant_alternativas=None,
                         atividade=None):
    acao = request.POST.get('acao', '')

    turma_form = (turma_cadastro(request.POST)
                  if acao == 'turma-salvar'
                  else TurmaForm())

    documento_form, tipo_form = (documento_cadastro(request)
                                 if (acao == 'documento-salvar' or
                                     acao == 'tipo-salvar')
                                 else (DocumentoForm(prefix='documento'),
                                       TipoForm(prefix='tipo')))

    atividade_form = AtividadeForm(request.POST or None,
                                   instance=atividade)
    if acao != 'salvar':
        for field in atividade_form.fields:
            atividade_form.errors[field] = atividade_form.error_class()

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
        questao_form = QuestaoForm(request.POST or None,
                                   prefix="questao%d" % n,
                                   instance=questao)
        questoes_forms.append(questao_form)
        if acao != 'salvar':
            for field in questao_form.fields:
                questao_form.errors[field] = questao_form.error_class()
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
            alternativa_form = AlternativaForm(
                request.POST or None,
                prefix="alternativa%d-q%d" % (m, n),
                instance=alternativa)
            alternativas_forms.append(alternativa_form)
            if acao != 'salvar':
                for field in alternativa_form.fields:
                    alternativa_form.errors[field] = alternativa_form.error_class(
                    )
        # Armazenada as listas na outra
        alternativas_forms_questao.append(alternativas_forms)

    valido = (acao == 'salvar' and
              atividade_form.is_valid() and
              all([questao_form.is_valid()
                   for questao_form in questoes_forms]) and
              all([alternativa_form.is_valid()
                   for alternativa_form in alternativas_forms
                   for alternativas_forms in alternativas_forms_questao]))
    if valido:
        atividade = atividade_form.save()
        for questao_form, alternativas_forms in zip(
                questoes_forms,
                alternativas_forms_questao):
            questao = questao_form.save(commit=False)
            questao.atividade = atividade
            questao.save()
            questao_form.save_m2m()

            for alternativa_form in alternativas_forms:
                alternativa = alternativa_form.save(commit=False)
                alternativa.questao = questao
                alternativa.save()
        return redirect('atividade', atividade.id)
    contexto = {
        'turma_form': turma_form,
        'documento_form': documento_form,
        'tipo_form': tipo_form,
        'atividade_form': atividade_form,
        'questoes_forms': questoes_forms,
        'alternativas_forms_questao': alternativas_forms_questao,
        'titulo': titulo,
        'csrf_token': get_token(request),
    }
    return render(request, 'atividade_cadastro.html', contexto)


@login_required
@permission_required('core.add_atividade', raise_exception=True)
@permission_required('core.add_questao', raise_exception=True)
@permission_required('core.add_alternativa', raise_exception=True)
def atividade_cadastro(request):
    return atividade_formulario(request, 'Cadastrar uma nova atividade')


@login_required
@permission_required('core.view_atividade', raise_exception=True)
@permission_required('core.view_questao', raise_exception=True)
@permission_required('core.view_alternativa', raise_exception=True)
def atividade(request, id):
    atividade = get_object_or_404(Atividade, pk=id)
    contexto = {
        'atividade': atividade,
        'agora': agora,
    }
    if request.user.is_professor():
        return render(request, 'atividade.html', contexto)

    grupo = request.user.get_grupo(atividade)
    if not grupo:
        return redirect('grupo_cadastro', id)

    forms = []
    for n, questao in enumerate(atividade.questao_set.all(), start=1):
        resposta, criada = Resposta.objects.get_or_create(grupo=grupo,
                                                          questao=questao)
        forms.append(RespostaForm(resposta,
                                  request.POST or None,
                                  prefix="questao%s" % n,
                                  use_required_attribute=False))

    if 'acao' in request.POST:
        acao = request.POST['acao']
        if acao == 'salvar' or acao == 'enviar':
            for form in forms:
                if form.is_valid():
                    form.save(enviar=(acao == 'enviar'))

    contexto['forms'] = forms
    return render(request, 'atividade_responder.html', contexto)


@login_required
@permission_required('core.change_atividade', raise_exception=True)
@permission_required('core.change_questao', raise_exception=True)
@permission_required('core.change_alternativa', raise_exception=True)
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
@permission_required('core.delete_atividade', raise_exception=True)
@permission_required('core.delete_questao', raise_exception=True)
@permission_required('core.delete_alternativa', raise_exception=True)
def atividade_remocao(request, id):
    atividade = get_object_or_404(Atividade, pk=id)
    atividade.delete()
    return redirect('perfil')


def gerar_notas(request, atividade_id):
    grupos = Grupo.objects.filter(atividade__id=atividade_id)
    atividade = grupos[0].atividade
    nota_total = atividade.questao_set.aggregate(Sum('peso'))['peso__sum']
    for grupo in grupos:
        nota = 0
        for questao in atividade.questao_set.all():
            resposta = Resposta.objects.get(grupo=grupo, questao=questao)
            if resposta.enviada:
                nota += resposta.escolha.peso * questao.peso
        nota *= 20 / nota_total
        grupo.nota = nota
        grupo.save()
    return redirect('atividade', atividade_id)


@login_required
@permission_required('core.view_grupo', raise_exception=True)
def grupos(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    grupos = Grupo.objects.filter(atividade__id=atividade_id)
    sem_grupo = Usuario.objects.filter(groups__name__startswith="A",
                                       grupo__isnull=True)
    contexto = {
        'grupos': grupos,
        'titulo': "Grupos da atividade %s" % atividade,
        'sem_grupo': sem_grupo,
    }
    return render(request, 'grupos.html', contexto)


@login_required
@permission_required('core.add_grupo', raise_exception=True)
def grupo_cadastro(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    form = GrupoCriacaoForm(atividade, request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('grupos', atividade_id)
    contexto = {
        'form': form,
        'titulo': "Cadastro de grupo para a atividade \"%s\"" % atividade,
    }
    return render(request, 'grupo_cadastro.html', contexto)


@login_required
@permission_required('core.change_grupo', raise_exception=True)
def grupo_edicao(request, id):
    grupo = get_object_or_404(Grupo, pk=id)
    form = GrupoEdicaoForm(request.POST or None, instance=grupo)
    if form.is_valid():
        form.save()
        return redirect('grupos', grupo.atividade.id)
    contexto = {
        'form': form,
        'titulo': "Edição de grupo para a atividade \"%s\"" % grupo.atividade,
    }
    return render(request, 'grupo_cadastro.html', contexto)


@login_required
@permission_required('core.delete_grupo', raise_exception=True)
def grupo_remocao(request, id):
    grupo = get_object_or_404(Grupo, pk=id)
    atividade_id = grupo.atividade.id
    grupo.delete()
    return redirect('grupos', atividade_id)


@login_required
@permission_required('core.view_documento', raise_exception=True)
@permission_required('core.view_tipo', raise_exception=True)
def documentos(request):
    documentos = Documento.objects.all()
    contexto = {
        'documentos': documentos,
    }
    return render(request, 'documentos.html', contexto)


@login_required
@permission_required('core.add_documento', raise_exception=True)
@permission_required('core.add_tipo', raise_exception=True)
def documento_cadastro(request):
    acao = request.POST.get('acao', '')
    tipo_form = (TipoForm(request.POST, prefix='tipo')
                 if acao == 'tipo-salvar'
                 else TipoForm(prefix='tipo'))
    if tipo_form.is_valid():
        tipo_form.save()

    composicao = request.POST.get('documento-composicao', '')
    if composicao == 0:
        request.POST['documento-arquivo'] = None
    elif composicao == 1:
            request.POST['documento-texto'] = None
    documento_form = (DocumentoForm(request.POST,
                                    request.FILES,
                                    prefix='documento')
                      if acao == 'documento-salvar'
                      else DocumentoForm(prefix='documento'))
    if documento_form.is_valid():
        documento_form.save()
        documento_form.data = {}

    return documento_form, tipo_form
