from django import forms

from .models import (Turma, Atividade, Grupo, Tipo,
                     Usuario, Documento, Questao, Alternativa)


def get_proper_date_time_input():
    return forms.DateTimeInput(
        format='%d/%m/%Y %H:%M',
        attrs={'placeholder': 'dd/mm/aaaa h:m'}
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
