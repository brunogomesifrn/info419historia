from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import (UsuarioForm, TurmaForm, AtividadeForm,
                    TipoForm, DocumentoForm, QuestaoForm, AlternativaForm)
from .models import Turma, Atividade, Grupo, Documento, Questao, Alternativa
from django.http import HttpResponse

# Create your views here.


def inicio(request):
    contexto = {
        'current': 'inicio'
    }
    return render(request, 'index.html', contexto)


@login_required
def perfil(request):
    return render(request, 'perfil.html')


def usuarios(request):
  usuarios = User.objects.order_by('nome')
  contexto = {
      'usuarios': usuarios,
  }
  return render(request, 'usuarios.html', contexto)


def registro(request):
    form = UsuarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    contexto = {
        'form': form,
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
def atividade_cadastro(request):
  # Ação recebida pelo formulário
  acao = request.POST['acao'] if 'acao' in request.POST else ''

  atividade_form = AtividadeForm(
      request.POST or None, use_required_attribute=False)

  # A quantidade de questões, inicialmente, é um, mas pode mudar de acordo com o valor recebido pelo formulário e se a ação for nova questão ou remover
  quant_questoes = 1
  if 'quant_questoes' in request.POST:
    quant_questoes = int(request.POST['quant_questoes'])
  if acao == "nova_questao":
    quant_questoes += 1
  elif acao == "remover_questao":
    quant_questoes -= 1

  # A quantidade de alternativas é uma lista porque podem existir diversas questões na mesma página. O índice 0 corresponde à questão 1, o 1 à 2 etc. Todas as questões começam com 2 alternativas, mas podem mudar pelo valor recebido ou pela ação.
  quant_alternativas = [2] * quant_questoes
  # O laço vai de 1 a quantidade de questões
  for questao in range(1, quant_questoes + 1):
    if 'quant_alternativas-q%d' % questao in request.POST:
      quant_alternativas[questao -
                         1] = int(request.POST['quant_alternativas-q%d' % questao])
    if acao == "nova_alternativa-q%d" % questao:
      quant_alternativas[questao - 1] += 1
    elif acao == "remover_alternativa-q%d" % questao:
      quant_alternativas[questao - 1] -= 1

  # Como existem diversas questões e alternativas, também serão necessários diversos formulários, armazenados em listas.
  questoes_forms = []
  # O índice 0 dessa lista irá armazenar uma outra lista com os formulários das alternativas da questão 1, o 1 uma com os da questão 2 etc.
  alternativas_forms_questao = []
  for n in range(1, quant_questoes + 1):
    # É armazemado um formulário para cada questão, todos dentro da lista "questoes_forms". O parâmetro "prefix" serve pata nomear cada formulário e evitar que os dados sejam misturados. As questões são nomeadas "questao1", "questao2", ...
    questoes_forms.append(QuestaoForm(
        request.POST or None, prefix="questao%d" % n, use_required_attribute=False))
    # Essa lista armazenará somente os formulários as alternativas da mesma questão
    alternativas_forms = []
    # O laço vai de 1 a quantidade de alternativas da questão n
    for m in range(1, quant_alternativas[n - 1] + 1):
      # Arzenados os formulários das alternativas com o prefix "alternativa1-q1", "alternativa2-q1", ..., "alternativa1-q2", "alternativa2-q2", ...
      alternativas_forms.append(AlternativaForm(request.POST or None, prefix="alternativa%d-q%d" % (m, n), use_required_attribute=False)
                                )
    # Armazenada as listas na outra
    alternativas_forms_questao.append(alternativas_forms)

  # Testando se a ação recebida foi de salvar os dados e se o formulário da atividade é válido
  if acao == 'salvar' and atividade_form.is_valid():
      # Salvando os dados do formulário da atividade e guardando o objeto criado em "atividade"
    atividade = atividade_form.save()
    # A função zip permite iterar sobre as duas listas ao mesmo tempo
    for questao_form, alternativas_forms in zip(questoes_forms, alternativas_forms_questao):
      if questao_form.is_valid():
        # Commit = false não deixa salvar os dados no banco, mas retorna um objeto
        questao = questao_form.save(commit=False)
        # É possível salvar o atributo restante e salvar corretamente
        questao.atividade = atividade
        questao.save()
        for alternativa_form in alternativas_forms:
          if alternativa_form.is_valid():
            alternativa = alternativa_form.save(commit=False)
            alternativa.questao = questao
            alternativa.save()
    return redirect('atividades')
  # Envia-se como contexto o formulário da atividade, a lista com os formulários das questões e a lista com as listas dos formulários das alternativas de cada questão
  contexto = {
      'atividade_form': atividade_form,
      'questoes_forms': questoes_forms,
      'alternativas_forms_questao': alternativas_forms_questao,
  }
  return render(request, 'atividade_cadastro.html', contexto)


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
