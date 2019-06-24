from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Turma, Atividade, Grupo, Tipo, Documento, Questao, Alternativa


def get_proper_date_time_input():
	return forms.DateTimeInput(
		format='%d/%m/%Y %H:%M',
		attrs = {'placeholder':'dd/mm/aaaa h:m'}
	)


class UsuarioForm(UserCreationForm):
	nome = forms.CharField(label='Nome', max_length=100)
	matricula = forms.CharField(label='Matrícula', max_length=14)
	email = forms.EmailField(label='Email')
	professor = forms.BooleanField(label='Professor')


	class Meta:
		model = User
		fields = ['nome', 'username', 'matricula', 'email', 'professor', 'password1', 'password2']

	def save(commit=True):
		usuario = super(UserCreationForm, self).save(commit=False)
		usuario.nome = self.cleaned_data['nome']
		usuario.matricula = self.cleaned_data['matricula']
		usuario.email = self.cleaned_data['email']
		usuario.professor = self.cleaned_data['professor']

		if commit:
			user.save()
		return usuario



class TurmaForm(forms.ModelForm):
	class Meta:
		model = Turma
		fields = ['nome', 'membros']


class AtividadeForm(forms.ModelForm):
	class Meta:
		model = Atividade
		fields = ['assunto', 'peso', 'inicio', 'fim', 'turmas']
		widgets = {
			'inicio': get_proper_date_time_input(),
			'fim': get_proper_date_time_input(),
		}


class GrupoForm(forms.ModelForm):
	class Meta:
		model = Grupo
		fields = ['membros']


class TipoForm(forms.ModelForm):
	class Meta:
		model = Tipo
		fields = ['nome']


class DocumentoForm(forms.ModelForm):
	class Meta:
		model = Documento
		fields = ['titulo', 'origem', 'creditos', 'texto', 'arquivo', 'tipo']


class QuestaoForm(forms.ModelForm):
	class Meta:
		model = Questao
		fields = ['comando', 'peso', 'documentos']


class AlternativaForm(forms.ModelForm):
	class Meta:
		model = Alternativa
		fields = ['texto', 'peso']