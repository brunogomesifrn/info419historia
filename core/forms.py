from django import forms
from .models import Usuario, Turma, Atividade, Grupo, Documento, Questao, Alternativa

		
def get_proper_date_time_input():
	return forms.DateTimeInput(
		format='%d/%m/%Y %H:%M',
		attrs = {'placeholder':'dd/mm/aaaa h:m'}
	)


class UsuarioForm(forms.ModelForm):
	class Meta:
		model = Usuario
		fields = ['nome', 'matricula', 'email', 'professor']


class TurmaForm(forms.ModelForm):
	class Meta:
		model = Turma
		fields = ['nome', 'membros']


class AtividadeForm(forms.ModelForm):
	class Meta:
		model = Atividade
		fields = ['peso', 'inicio', 'fim']
		widgets = {
			'inicio': get_proper_date_time_input(),
			'fim': get_proper_date_time_input(),
		}


class GrupoForm(forms.ModelForm):
	class Meta:
		model = Grupo
		fields = ['membros']


class DocumentoForm(forms.ModelForm):
	class Meta:
		model = Documento
		fields = ['texto', 'arquivo']


class QuestaoForm(forms.ModelForm):
	prefix = 'questao'
	class Meta:
		model = Questao
		fields = ['comando', 'peso', 'documentos', 'atividade']
		widgets = {
			'atividade': forms.HiddenInput(),
		}


class AlternativaForm(forms.ModelForm):
	prefix = 'alternativa'
	class Meta:
		model = Alternativa
		fields = ['texto', 'peso', 'questao']
		widgets = {
			'questao': forms.HiddenInput(),
		}