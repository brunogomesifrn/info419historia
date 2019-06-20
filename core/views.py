from django.shortcuts import render, redirect
from .forms import UsuarioForm, AtividadeForm
from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa

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
	form = AtividadeForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('atividades')
	contexto = {
		'form': form
	}
	return render(request, 'atividade_cadastro.html', contexto)

def atividade(request, id):
	atividade = Atividade.objects.get(pk=id)
	questoes = Questao.objects.filter(atividade=atividade)
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