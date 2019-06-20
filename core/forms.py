from django.forms import ModelForm
from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa


class UsuarioForm(ModelForm):
	class Meta:
		model = Usuario
		fields = ['nome', 'matricula', 'email', 'professor']


class TurmaForm(ModelForm):
	class Meta:
		model = Turma
		fields = ['nome', 'membros']


class AtividadeForm(ModelForm):
	class Meta:
		model = Atividade
		fields = ['peso', 'inicio', 'fim']


class GrupoForm(ModelForm):
	class Meta:
		model = Grupo
		fields = ['membros']


class DocumentoForm(ModelForm):
	class Meta:
		model = Documento
		fields = ['texto', 'arquivo']


class QuestaoForm(ModelForm):
	class Meta:
		model = Questao
		fields = ['comando', 'peso', 'atividade', 'documentos']


class AlternativaForm(ModelForm):
	class Meta:
		model = Alternativa
		fields = ['texto', 'peso', 'questao']