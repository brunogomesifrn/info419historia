from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsuarioForm, AtividadeForm, DocumentoForm, QuestaoForm, AlternativaForm
from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa
from django.core import serializers
from django.http import QueryDict

# Create your views here.
def home(request):
	return render(request, 'index.html')

def usuarios(request):
	usuarios = Usuario.objects.order_by('nome')
	contexto = {
		'usuarios': usuarios,
	}
	return render(request, 'usuarios.html', contexto)

def turmas(request):
	turmas = Turma.objects.order_by('nome')
	contexto = {
		'turmas': turmas,
	}
	return render(request, 'turmas.html', contexto)

def atividades(request):
	atividades = Atividade.objects.all()
	contexto = {
		'atividades': atividades,
	}
	return render(request, 'atividades.html', contexto)

def atividade_cadastro(request):
	form = AtividadeForm(request.POST or None, instance=get_model_from_session(request, 'atividade'))
	if form.is_valid():
		atividade = form.save(commit=False)
		request.session['atividade'] = serializers.serialize("json", [atividade])
		return redirect('questao_cadastro', permanent=True)
	contexto = {
		'form': form
	}
	return render(request, 'atividade_cadastro.html', contexto)

def questao_cadastro(request):
	if not request.session['atividade']:
		return redirect('atividade_cadastro', permanent=True)
	form = QuestaoForm(request.POST or None)
	if form.is_valid():
		questao = form.save(commit=False)
		request.session['questao'] = serializers.serialize("json", [questao])
		return redirect('alternativa_cadastro')
	contexto = {
		'form': form,
		#'atividade_hidden_form': atividade_hidden_form,
	}
	return render(request, 'questao_cadastro.html', contexto)
		

def alternativa_cadastro(request):
	if not request.session['questao']:
		return redirect('questao_cadastro', permanent=True)
	form = AlternativaForm(request.POST or None)
	if form.is_valid():
		aternativa = form.save(commit=False)
		questao = get_model_from_session(request, 'questao')
		atividade = get_model_from_session(request, 'atividade')

		atividade.save()

		questao.atividade = atividade
		questao.save()

		alternativa.questao = questao
		alternativa.save()
		return redirect('alternativa_cadastro')
	contexto = {
		'form': form,
		'questao_hidden_form': questao_hidden_form,
	}
	return render(request, 'alternativa_cadastro.html', contexto)


def atividade(request, id):
	atividade = get_object_or_404(Atividade, pk=id)
	questoes = atividade.questao_set.all()
	contexto = {
		'atividade': atividade,
		'questoes': questoes,
	}
	return render(request, 'atividade.html', contexto)


def grupos(request):
	grupos = Grupo.objects.all()
	contexto = {
		'grupos': grupos,
	}
	return render(request, 'grupos.html', contexto)

def documentos(request):
	documentos = Documento.objects.all()
	contexto = {
		'documentos': documentos,
	}
	return render(request, 'documentos.html', contexto)

def documento_cadastro(request):
	form = DocumentoForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('atividade_cadastro')
	contexto = {
		'form': form
	}
	return render(request, 'documento_cadastro.html', contexto)

def get_model_from_session(request, name):
	return QueryDict(request.session[name]) if request.session[name] else None
