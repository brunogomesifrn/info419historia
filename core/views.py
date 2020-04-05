from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import (
    PermissionDenied, ValidationError, ObjectDoesNotExist
)
from django.db.models import Prefetch, Q, F, OuterRef, Subquery
from django.db.models.aggregates import Sum, Count
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.http import JsonResponse
from . import models, forms

agora = timezone.now()


@login_required
def perfil(request):
    turmas = models.Turma.objects.filter(membros=request.user)
    atividades = models.Atividade.objects.filter(turmas__in=turmas).distinct()

    contexto = {
        'turmas': turmas,
        'atividades': atividades,
        'agora': agora
    }

    if request.user.is_professor:
        return render(request, 'perfil_professor.html', contexto)

    atividades = atividades.filter(inicio__lte=agora)
    disponiveis = atividades.filter(fim__gte=agora)

    participacoes = models.Participacao.objects.filter(
        grupo__atividade__in=disponiveis,
        aluno=request.user
    ).annotate(
        n_pendencias=Count(
            'grupo__participacoes',
            filter=Q(grupo__participacoes__confirmado=False)
        )
    ).select_related('grupo', 'grupo__atividade', 'grupo__criador') \
     .only(
        'grupo', 'confirmado', 'aluno', 'grupo__atividade',
        'grupo__criador__nome', 'grupo__atividade__assunto'
    )

    sem_grupo = disponiveis.exclude(grupos__participacoes__in=participacoes) \
                           .annotate(
                               n_grupos_atual=Count('grupos', distinct=True))
    terminadas = atividades.filter(fim__lte=agora).prefetch_related(
        Prefetch(
            'grupos',
            queryset=models.Grupo.objects.filter(membros=request.user)
                                         .only('nota', 'atividade'),
            to_attr='grupo'
        )
    )

    contexto.update({
        'participacoes': participacoes,
        'sem_grupo': sem_grupo,
        'terminadas': terminadas,
    })

    # contexto['atividades'] = (
    #     atividades.filter(inicio__lte=agora).annotate(
    #         Subquery(
    #             models.Participacao.objects.filter(
    #                 grupo__atividade=OuterRef('pk'),
    #                 aluno=request.user
    #             ).only('id'),
    #         n_grupos_atual=Count('grupos', distinct=True)
    #         )
    #     )
    # )
    # .prefetch_related(
    #     Prefetch(
    #         'grupos',
    #         queryset=(
    #             models.Grupo.objects.filter(
    #                 participacoes__aluno=request.user
    #             )
    #             .annotate(
    #                 n_pendencias=Count(
    #                     'participacoes',
    #                     filter=Q(participacoes__confirmado=False)
    #                 )
    #             )
    #             .select_related('criador')
    #         ),
    #         to_attr='grupo'
    #     ),
    #     Prefetch(
    #         'grupo__participacoes',
    #         queryset=models.Participacao.objects.filter(aluno=request.user),
    #         to_attr='participacao',
    #     ),
    # )
    return render(request, 'perfil_aluno.html', contexto)


# decrepated
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
    usuarios = models.Usuario.objects.order_by('nome')
    contexto = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios.html', contexto)


def registro(request):
    form = forms.UsuarioCriacaoForm(request.POST or None)
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
    usuario = get_object_or_404(models.Usuario, pk=id)
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
    form = forms.UsuarioEdicaoForm(request.POST or None, instance=usuario)
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
    usuario = get_object_or_404(models.Usuario, pk=id)
    usuario.delete()
    return render(request, 'usuarios.html')


@login_required
@permission_required('core.view_turma', raise_exception=True)
def turma(request, id):
    turma = get_object_or_404(models.Turma, pk=id)
    contexto = {
        'turma': turma,
    }
    return render(request, 'turma.html', contexto)


@login_required
@permission_required('core.add_turma', raise_exception=True)
def turma_cadastro(request):
    form = forms.TurmaForm(data=request.POST or None)
    if form.is_valid():
        turma = form.save()
        return JsonResponse({'id': turma.id})
    contexto = {
        'form': form
    }
    return render(request, 'form.html', contexto)


@login_required
@permission_required('core.change_turma', raise_exception=True)
def turma_edicao(request, id):
    turma = get_object_or_404(models.Turma, pk=id)
    form = forms.TurmaForm(data=request.POST or None, instance=turma)
    if form.is_valid():
        form.save()
        return redirect('turma', id)
    contexto = {
        'form': form
    }
    return render(request, 'form.html', contexto)


@login_required
@permission_required('core.delete_turma', raise_exception=True)
def turma_remocao(request, id):
    turma = get_object_or_404(models.Turma, pk=id)
    turma.delete()
    return redirect('perfil')


def atividade_formulario(request,
                         titulo,
                         atividade=None):
    atividade_form = forms.AtividadeForm(data=request.POST or None,
                                         instance=atividade)
    if atividade_form.is_valid():
        atividade = atividade_form.save()
        return redirect('atividade', atividade.id)

    contexto = {
        'atividade_form': atividade_form,
        'titulo': titulo,
    }
    return render(request, 'atividade_cadastro.html', contexto)


@login_required
@permission_required('core.add_atividade', raise_exception=True)
@permission_required('core.add_questao', raise_exception=True)
@permission_required('core.add_alternativa', raise_exception=True)
def atividade_cadastro(request):
    return atividade_formulario(request, 'Cadastrar uma nova atividade')


@login_required
@permission_required('core.change_atividade', raise_exception=True)
@permission_required('core.change_questao', raise_exception=True)
@permission_required('core.change_alternativa', raise_exception=True)
def atividade_edicao(request, id):
    atividade = get_object_or_404(models.Atividade, pk=id)

    if atividade.fim > agora:
        return atividade_formulario(request, 'Editar atividade', atividade)

    messages.add_message(
        request,
        messages.ERROR,
        'Não é possível editar uma atividade que já acabou'
    )

    return redirect('perfil')


@login_required
@permission_required('core.view_atividade', raise_exception=True)
@permission_required('core.view_questao', raise_exception=True)
@permission_required('core.view_alternativa', raise_exception=True)
def atividade(request, id):
    atividade = get_object_or_404(models.Atividade, pk=id)
    contexto = {
        'atividade': atividade,
        'agora': agora,
    }
    if request.user.is_professor:
        return render(request, 'atividade.html', contexto)
    participacao = request.user.get_participacao(atividade)
    if not participacao:
        messages.add_message(
            request,
            messages.ERROR,
            "Você precisa estar em um grupo para resolver a atividade"
        )
        return redirect('perfil')

    formset = forms.RespostaFormSet(
        grupo=participacao.grupo, data=request.POST or None
    )

    acao = request.POST.get('acao')
    if acao == 'salvar' or acao == 'enviar':
        if formset.is_valid():
            formset.save()
            return redirect('atividade', id)
    contexto.update({
        'formset': formset,
        'participacao': participacao
    })
    return render(request, 'atividade_responder.html', contexto)


@login_required
@permission_required('core.delete_atividade', raise_exception=True)
@permission_required('core.delete_questao', raise_exception=True)
@permission_required('core.delete_alternativa', raise_exception=True)
def atividade_remocao(request, id):
    atividade = get_object_or_404(models.Atividade, pk=id)
    if atividade.fim > agora:
        atividade.delete()
    else:
        messages.add_message(
            request,
            messages.ERROR,
            'Não é possível apagar uma atividade que já acabou'
        )

    return redirect('perfil')


def gerar_notas(request, atividade_id):
    atividade = get_object_or_404(models.Atividade, pk=atividade_id)
    grupos = models.Grupo.objects.filter(
        atividade__pk=atividade_id
    ).prefetch_related(
        Prefetch(
            'participacoes',
            queryset=models.Participacao.objects.filter(confirmado=False),
            to_attr='nao_confirmados'
        )
    )
    nota_total = atividade.questoes.aggregate(Sum('peso'))['peso__sum']
    sem_grupo = models.Usuario.objects.filter(groups__name="Alunos")
    for grupo in grupos:
        for participacao in grupo.nao_confirmados:
            participacao.delete()
        sem_grupo = sem_grupo.exclude(pk__in=grupo.membros.all())
        nota = 0
        for questao in atividade.questoes.all():
            try:
                resposta = models.Resposta.objects.get(
                    grupo=grupo, questao=questao
                )
                if resposta.enviada:
                    nota += resposta.escolha.peso * questao.peso
            except ObjectDoesNotExist:
                pass
        nota *= 20 / nota_total
        grupo.nota = nota
        grupo.save()
    grupo = models.Grupo.objects.create(
        atividade=atividade, nota=0, criador=sem_grupo.first()
    )
    for aluno in sem_grupo:
        participacao = models.Participacao.objects.create(
            grupo=grupo,
            aluno=aluno,
            confirmado=True
        )

    return redirect('atividade', atividade_id)


@login_required
@permission_required('core.view_grupo', raise_exception=True)
def grupos(request, atividade_id):
    atividade = get_object_or_404(models.Atividade, pk=atividade_id)
    grupos = models.Grupo.objects.filter(atividade__id=atividade_id)

    contexto = {
        'grupos': grupos
    }

    if not request.user.is_professor:
        return render(request, 'entrar_grupo.html', contexto)

    sem_grupo = models.Usuario.objects.filter(groups__name="Alunos",
                                              grupos__isnull=True)
    contexto.update({
        'titulo': "Grupos da atividade %s" % atividade,
        'sem_grupo': sem_grupo,
    })
    return render(request, 'grupos.html', contexto)


@login_required
@permission_required('core.add_grupo', raise_exception=True)
def grupo_cadastro(request, atividade_id):
    atividade = get_object_or_404(models.Atividade, pk=atividade_id)
    grupo = models.Grupo(atividade=atividade)
    participacao = models.Participacao(
        grupo=grupo,
        aluno=request.user,
        criador=True,
        confirmado=True
    )
    try:
        grupo.full_clean()
        participacao.full_clean(exclude=('grupo',))
        grupo.save()
        participacao.grupo = grupo
        participacao.save()
    except ValidationError as e:
        for erros in e.message_dict.values():
            for erro in erros:
                messages.add_message(request, messages.ERROR, erro)
        return redirect('perfil')
    return redirect('atividade', atividade.id)


def entrar_grupo(request, id):
    grupo = get_object_or_404(models.Grupo.select_related('criador'), pk=id)
    participacao = models.Participacao(
        grupo=grupo,
        aluno=request.user
    )
    try:
        participacao.full_clean(exclude=('grupo',))
        participacao.save()
        messages.add_message(
            request,
            messages.INFO,
            "Aguare %s confirmar a sua participação no grupo" % (
                grupo.criador.nome
            )
        )
    except ValidationError as e:
        for erros in e.message_dict.values():
            for erro in erros:
                messages.add_message(request, messages.ERROR, erro)
    return redirect('perfil')


@login_required
def sair_grupo(request, id):
    participacao = get_object_or_404(
        models.Participacao.objects.select_related('grupo')
                                   .annotate(n_membros=Count(
                                       'grupo__participacoes'
                                   )),
        grupo__pk=id, aluno__pk=request.user.id
    )
    grupo = participacao.grupo
    if participacao.n_membros == 1:
        grupo.delete()
        mensagem = "Você saiu do grupo e ele foi excluído"
    else:
        participacao.delete()
        if participacao.is_criador:
            mensagem = "Você saiu do grupo e agora %s o administra" % (
                participacao.grupo.criador.nome
            )
        else:
            mensagem = "Você saiu do %s" % grupo
    messages.add_message(request, messages.INFO, mensagem)
    return redirect('perfil')


@login_required
@permission_required('core.change_grupo', raise_exception=True)
def grupo_edicao(request, id):
    grupo = get_object_or_404(models.Grupo, pk=id)
    form = forms.GrupoEdicaoForm(request.POST or None, instance=grupo)
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
    grupo = get_object_or_404(models.Grupo, pk=id)
    atividade_id = grupo.atividade.id
    grupo.delete()
    return redirect('grupos', atividade_id)


@login_required
def grupo_aceitar(request, grupo_id, aluno_id):
    participacao = models.Participacao.objects.get(
        grupo__pk=grupo_id, aluno__pk=aluno_id
    )
    participacao.confirmado = True
    participacao.save()
    messages.add_message(
        request,
        messages.INFO,
        "%s entrou grupo" % participacao.aluno.nome
    )
    return redirect('atividade', participacao.grupo.atividade.id)


@login_required
def grupo_rejeitar(request, grupo_id, aluno_id):
    participacao = models.Participacao.objects.get(
        grupo__pk=grupo_id, aluno__pk=aluno_id
    )
    participacao.delete()
    messages.add_message(
        request,
        messages.INFO,
        "%s não entrou no grupo" % participacao.aluno.nome
    )
    return redirect('atividade', participacao.grupo.atividade.id)


@login_required
@permission_required('core.view_documento', raise_exception=True)
@permission_required('core.view_tipo', raise_exception=True)
def documentos(request):
    documentos = models.Documento.objects.all()
    contexto = {
        'documentos': documentos,
    }
    return render(request, 'documentos.html', contexto)


@login_required
@permission_required('core.add_documento', raise_exception=True)
@permission_required('core.add_tipodocumento', raise_exception=True)
def documento_cadastro(request):
    data = request.POST.copy()

    tipo_form = forms.TipoDocumentoForm(data=data or None)
    if tipo_form.is_valid():
        tipo = tipo_form.save()
        data['documento-tipo'] = tipo.pk

    form = forms.DocumentoForm(
        data=data or None,
        files=request.FILES or None
    )
    if form.is_valid():
        documento = form.save()
        return JsonResponse({'id': documento.id})
    contexto = {
        'form': form,
        'tipo_form': tipo_form,
    }
    return render(request, 'documento_cadastro.html', contexto)
