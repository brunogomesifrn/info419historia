from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsuarioForm, TurmaForm, AtividadeForm, DocumentoForm, QuestaoForm, AlternativaForm
from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa
from django.core import serializers

# Create your views here.
def home(request):
	return render(request, 'index.html')

def usuarios(request):
	usuarios = Usuario.objects.order_by('nome')
	contexto = {
		'usuarios': usuarios,
	}
	return render(request, 'usuarios.html', contexto)

def usuario_cadastro(request):
	form = UsuarioForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('usuarios')
	contexto = {
		'form': form
	}
	return render(request, 'usuario_cadastro.html', contexto)

def turmas(request):
	turmas = Turma.objects.order_by('nome')
	contexto = {
		'turmas': turmas,
	}
	return render(request, 'turmas.html', contexto)

def turma_cadastro(request):
	form = TurmaForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('turmas')
	contexto = {
		'form': form
	}
	return render(request, 'turma_cadastro.html', contexto)

def atividades(request):
	atividades = Atividade.objects.all()
	contexto = {
		'atividades': atividades,
	}
	return render(request, 'atividades.html', contexto)

def atividade_cadastro(request):
	# Ação recebida pelo formulário
	acao = request.POST['acao'] if 'acao' in request.POST else ''

	atividade_form = AtividadeForm(request.POST or None)

	# A quantidade de questões, inicialmente, é um, mas pode mudar de acordo com o valor recebido pelo formulário e se a ação for nova questão ou remover
	quant_questoes = 1
	if 'quant_questoes' in request.POST: quant_questoes = int(request.POST['quant_questoes'])
	if acao == "nova_questao": quant_questoes += 1
	elif acao == "remover_questao": quant_questoes -= 1

	# A quantidade de alternativas é uma lista porque podem existir diversas questões na mesma página. O índice 0 corresponde à questão 1, o 1 à 2 etc. Todas as questões começam com 2 alternativas, mas podem mudar pelo valor recebido ou pela ação.
	quant_alternativas = [2] * quant_questoes
	# O laço vai de 1 a quantidade de questões
	for questao in range(1, quant_questoes+1):
		if 'quant_alternativas-q%d' % questao in request.POST: quant_alternativas[questao-1] = int(request.POST['quant_alternativas-q%d' % questao])
		if acao == "nova_alternativa-q%d" % questao: quant_alternativas[questao-1] += 1
		elif acao == "remover_alternativa-q%d" % questao: quant_alternativas[questao-1] -= 1

	# Como existem diversas questões e alternativas, também serão necessários diversos formulários, armazenados em listas.
	questoes_forms = []
	# O índice 0 dessa lista irá armazenar uma outra lista com os formulários das alternativas da questão 1, o 1 uma com os da questão 2 etc.
	alternativas_forms_questao = []
	for n in range(1, quant_questoes+1):
		# É armazemado um formulário para cada questão, todos dentro da lista "questoes_forms". O parâmetro "prefix" serve pata nomear cada formulário e evitar que os dados sejam misturados. As questões são nomeadas "questao1", "questao2", ...
		questoes_forms.append(QuestaoForm(request.POST or None, prefix="questao%d" % n))
		# Essa lista armazenará somente os formulários as alternativas da mesma questão
		alternativas_forms = []
		# O laço vai de 1 a quantidade de alternativas da questão n
		for m in range(1, quant_alternativas[n-1]+1):
			# Arzenados os formulários das alternativas com o prefix "alternativa1-q1", "alternativa2-q1", ..., "alternativa1-q2", "alternativa2-q2", ...
			alternativas_forms.append(AlternativaForm(request.POST or None, prefix="alternativa%d-q%d" % (m, n))
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