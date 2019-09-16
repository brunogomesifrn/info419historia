from django import forms
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

from .models import (Turma, Atividade, Grupo, Tipo, Usuario,
                     Documento, Questao, Alternativa)
__all__ = ['UsuarioCriacaoForm', 'UsuarioEdicaoForm', 'TurmaForm',
           'AtividadeForm', 'GrupoCriacaoForm', 'GrupoEdicaoForm', 'TipoForm',
           'DocumentoForm', 'QuestaoForm', 'AlternativaForm', 'RespostaForm']


class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        super().__init__(input_formats=['%Y-%m-%dT%H:%M'], *args, **kwargs)
        self.widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, nome, genero, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome = nome
        self.genero = genero
        self.attrs = {'class': 'form-check-input'}


class UsuarioCriacaoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('nome',
                  'sobrenome',
                  'matricula',
                  'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['nome'].widget.attrs.update({'autofocus': True})


class UsuarioEdicaoForm(UserChangeForm):
    password = None

    class Meta:
        model = Usuario
        fields = ('nome',
                  'sobrenome',
                  'matricula',
                  'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['nome'].widget.attrs.update({'autofocus': True})


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'membros']
        widgets = {
            'membros': CheckboxSelectMultiple('usuario', 'm'),
        }


class AtividadeForm(forms.ModelForm):
    inicio = DateTimeField()
    fim = DateTimeField()

    class Meta:
        model = Atividade
        fields = ['assunto', 'peso', 'inicio', 'fim', 'turmas']
        widgets = {
            'turmas': CheckboxSelectMultiple('turma', 'f'),
        }


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['membros']
        widgets = {
            'membros': CheckboxSelectMultiple('usuario sem grupo para essa atividade', 'm')
        }


class GrupoCriacaoForm(GrupoForm):
    def __init__(self, atividade, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['membros'].queryset = Usuario.objects.exclude(
            Q(groups__name__startswith="P") | Q(grupo__atividade=atividade))
        self.instance.atividade = atividade


class GrupoEdicaoForm(GrupoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            grupo = self.instance
            self.fields['membros'].queryset = Usuario.objects.exclude(
                Q(groups__name__startswith="P") |
                (Q(grupo__atividade=grupo.atividade) &
                    ~Q(grupo__id=grupo.id)))


class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['nome']


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'origem', 'creditos', 'texto', 'arquivo', 'tipo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].empty_label = "Nenhum"


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ['comando', 'peso', 'documentos']
        widgets = {
            'documentos': CheckboxSelectMultiple('documento', 'm'),
        }


class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ['texto', 'peso']


class RespostaForm(forms.Form):
    def __init__(self, resposta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resposta = resposta
        self.fields['alternativas'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=self.get_alternativas(),
            error_messages={'required': _('Não esqueça de responder essa questão!')})
        try:
            self.fields['alternativas'].initial = resposta.escolha.id
            if resposta.enviada:
                self.fields['alternativas'].widget.attrs['disabled'] = True
        except AttributeError:
            pass

    def get_alternativas(self):
        return [(alternativa.id, alternativa.texto)
                for alternativa in self.resposta.questao.alternativa_set.all()]

    def save(self, enviar=False):
        self.resposta.escolha_id = self.cleaned_data['alternativas']
        if enviar:
            self.resposta.enviada = True
        return self.resposta.save()
