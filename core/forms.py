from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# from .models import (Turma, Atividade, Grupo, Tipo,
#                      Usuario, Documento, Questao, Alternativa)
from .models import (Turma, Atividade, Tipo,
                     Usuario, Documento, Questao, Alternativa)


def get_proper_date_time_input():
    return forms.DateTimeInput(
        format='%d/%m/%Y %H:%M',
        attrs={'placeholder': 'dd/mm/aaaa hr:min'}
    )


class UsuarioCriacaoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('nome',
                  'sobrenome',
                  'matricula',
                  'professor',
                  'email',)


class UsuarioEdicaoForm(UserChangeForm):
    """docstring for UsuarioEdicaoForm"""
    class Meta:
        model = Usuario
        fields = ('nome',
                  'sobrenome',
                  'matricula',
                  'professor',
                  'email',)

# class UsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['email', 'password1', 'password2']


# class PerfilForm(forms.ModelForm):
#     class Meta:
#         model = Perfil
#         fields = ['nome', 'sobrenome', 'matricula', 'professor']


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'membros']
        widgets = {
            'membros': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['assunto', 'peso', 'inicio', 'fim', 'turmas']
        widgets = {
            'inicio': get_proper_date_time_input(),
            'fim': get_proper_date_time_input(),
            'turmas': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }


# class GrupoForm(forms.ModelForm):
#     class Meta:
#         model = Grupo
#         fields = ['membros']


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
        widgets = {
            'documentos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }


class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ['texto', 'peso']
