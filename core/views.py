from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import (UsuarioForm, TurmaForm, AtividadeForm,
                    TipoForm, DocumentoForm, QuestaoForm, AlternativaForm)
from .models import Turma, Atividade, Grupo, Documento, Questao, Alternativa
from django.http import HttpResponse

# Create your views here.


@login_required
def perfil(request):
  return render(request, 'perfil.html')


@login_required
def usuarios(request):
    usuarios = User.objects.order_by('nome')
    contexto = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios.html', contexto)


def registro(request):

    form = UsuarioForm(request.POST or None)
    user_form = UserCreationForm(request.POST or None)
    if form.is_valid() and user_form.is_valid():
        user = user_form.save()
        usuario = form.save(commit=False)
        usuario.user = user
        usuario.save()
        return redirect('login')
    contexto = {
        'form': form,
        'user_form': user_form,
    }
    return render(request, 'registration/registro.html', contexto)



@login_required
def usuario_edicao(request, id):
    usuario = get_object_or_404(User, pk=id)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if form.is_valid():
        form.save()
        return redirect('usuarios')
    contexto = {
        'form': form
    }
    return render(request, 'usuario_cadastro.html', contexto)


@login_required
def usuario_remocao(request, id):
    usuario = get_object_or_404(User, pk=id)
    usuario.delete()
    return render(request, 'usuarios.html')


@login_required
def turmas(request):
    turmas = Turma.objects.order_by('nome')
    contexto = {
        'turmas': turmas,
    }
    return render(request, 'turmas.html', contexto)


@login_required
def turma_cadastro(request):
    form = TurmaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('turmas')
    contexto = {
        'form': form
    }
    return render(request, 'turma_cadastro.html', contexto)


@login_required
def atividades(request):
    atividades = Atividade.objects.all()
    contexto = {
        'atividades': atividades,
    }
    return render(request, 'atividades.html', contexto)


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
def grupos(request):
    grupos = Grupo.objects.all()
    contexto = {
        'grupos': grupos,
    }
    return render(request, 'grupos.html', contexto)


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
    form = DocumentoForm(request.POST or None, use_required_attribute=False)
    tipo_form = TipoForm(request.POST or None, use_required_attribute=False)
    if tipo_form.is_valid():
        tipo = tipo_form.save()
        data = form.data.copy()
        data['tipo'] = tipo.id
        form = DocumentoForm(data)
    if form.is_valid():
        form.save()
        return redirect('atividade_cadastro')
    contexto = {
        'form': form,
        'tipo_form': tipo_form,
    }
    return render(request, 'documento_cadastro.html', contexto)
