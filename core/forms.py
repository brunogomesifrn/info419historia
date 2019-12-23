from django import forms
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
# from datetime import timezone
from . import models


def fix_date(date):
    return date.astimezone().strftime('%Y-%m-%dT%H:%M')


class ModelForm(forms.ModelForm):
    def __init__(self, save_name="salvar", *args, **kwargs):
        super().__init__(*args, **kwargs)
        acao = self.data.get('acao')
        self.save_name = save_name
        if acao != save_name:
            for name in self.fields:
                self.errors[name] = self.error_class()

    def is_valid(self):
        acao = self.data.get('acao')
        return acao == self.save_name and super().is_valid()


class BaseModelFormSet(forms.BaseModelFormSet):
    def __init__(self, save_name="salvar", *args, **kwargs):
        super().__init__(*args, **kwargs)
        acao = self.data.get('acao')
        self.save_name = save_name
        if acao != save_name:
            for form in self.forms:
                for name in form.fields:
                    form.errors[name] = form.error_class()

    def is_valid(self):
        acao = self.data.get('acao')
        return acao == self.save_name and super().is_valid()


class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        super().__init__(input_formats=['%Y-%m-%dT%H:%M'], *args, **kwargs)
        self.widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'})


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, nome, genero, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome = nome
        self.genero = genero
        self.attrs = {'class': 'form-check-input'}


class UsuarioCriacaoForm(UserCreationForm):
    class Meta:
        model = models.Usuario
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
        model = models.Usuario
        fields = ('nome',
                  'sobrenome',
                  'matricula',
                  'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['nome'].widget.attrs.update({'autofocus': True})


class TurmaForm(ModelForm):
    class Meta:
        model = models.Turma
        fields = ('nome', 'membros')
        widgets = {
            'membros': CheckboxSelectMultiple('usuario', 'm'),
        }

    def __init__(self, *args, **kwargs):
        kwargs['use_required_attribute'] = False
        super().__init__(*args, **kwargs)


class TipoDocumentoForm(ModelForm):
    class Meta:
        model = models.TipoDocumento
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        kwargs['use_required_attribute'] = False
        super().__init__(*args, **kwargs)
        self.prefix = "tipo"

    def validate_unique(self):
        pass

    def save(self):
        tipo, created = (
            models.TipoDocumento.objects.get_or_create(**self.cleaned_data)
        )
        return tipo


class DocumentoForm(ModelForm):
    class Meta:
        model = models.Documento
        fields = ('titulo', 'origem', 'creditos', 'tipo')

    class Texto(forms.ModelForm):
        class Meta:
            model = models.DocumentoTexto
            fields = ('texto',)

    class Arquivo(forms.ModelForm):
        class Meta:
            model = models.DocumentoArquivo
            fields = ('arquivo',)

    def __init__(self, data, *args, **kwargs):
        kwargs['use_required_attribute'] = False
        kwargs['prefix'] = "documento"
        kwargs['data'] = data

        super().__init__(*args, **kwargs)

        self.fields['tipo'].empty_label = "Nenhum"

        self.fields['composicao'] = forms.ChoiceField(
            choices=[
                (0, 'Texto'),
                (1, 'Arquivo')
            ],
            label="O documento será composto por",
            initial=0
        )
        self.fields['composicao'].empty_label = None

        self.fields.update(
            DocumentoForm.Texto(*args, **kwargs).fields
        )
        self.fields.update(
            DocumentoForm.Arquivo(*args, **kwargs).fields
        )
        self.fields['texto'].required = False
        self.fields['arquivo'].required = False

    def clean(self):
        data = super().clean()
        composicao = data.get('composicao')
        if composicao:
            if composicao == '0' and not data.get('texto'):
                self.add_error(
                    'texto',
                    '''É necessário definir um texto caso a
                    composição esteja selecionada como "Texto"'''
                )
            elif composicao == '1' and not data.get('arquivo'):
                self.add_error(
                    'arquivo',
                    '''É necessário escolher um arquivo caso a
                    composição esteja selecionada como "Arquivo"'''
                )

    def save(self):
        documento = super().save()

        composicao = self.cleaned_data.get('composicao')
        if composicao == '0':
            models.DocumentoTexto.objects.create(
                documento=documento,
                texto=self.cleaned_data.get('texto')
            )
        elif composicao == '1':
            models.DocumentoArquivo.objects.create(
                documento=documento,
                arquivo=self.cleaned_data.get('arquivo')
            )
        return documento


class AlternativaForm(ModelForm):
    peso = forms.IntegerField(min_value=0, max_value=5)

    class Meta:
        model = models.Alternativa
        fields = ['texto', 'peso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True, questao=None):
        if commit and not questao:
            raise TypeError("""save() missing 1 required
                               positional argument: 'questao'""")

        alternativa = super().save(commit=False)
        if commit:
            alternativa.questao = questao
            alternativa.save()
        return alternativa


class BaseAlternativaFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        acao = self.data.get('acao')
        if acao == self.prefix + '-adicionar':
            self.forms[-1].fields['texto'].widget.attrs.update({
                'autofocus': True
            })

    def save(self, commit=True, questao=None):
        alternativas = super().save(commit=False)
        if commit:
            for form in self.saved_forms:
                form.save(questao=questao)
            for form in self.deleted_forms:
                if not form.instance.pk:
                    continue
                self.deleted_objects.append(form.instance)
                form.instance.delete()
        return alternativas

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if index > 1:
            form.fields.move_to_end('DELETE', last=False)
        else:
            form.fields.pop('DELETE')


AlternativaFormSet = forms.modelformset_factory(
    models.Alternativa,
    form=AlternativaForm,
    formset=BaseAlternativaFormSet,
    can_delete=True,
    min_num=2,
    extra=0
)


class QuestaoForm(ModelForm):
    peso = forms.IntegerField(min_value=0)

    class Meta:
        model = models.Questao
        fields = ['comando', 'peso', 'documentos']
        widgets = {
            'documentos': CheckboxSelectMultiple('documento', 'm'),
        }

    def __init__(self, *args, **kwargs):
        self.alternativas = AlternativaFormSet()
        super().__init__(*args, **kwargs)

    def is_valid(self):
        return super().is_valid() and self.alternativas.is_valid()

    def save(self, commit=True, atividade=None):
        if commit and not atividade:
            raise TypeError("""save() missing 1 required
                                positional argument: 'atividade'""")

        questao = super().save(commit=False)
        if commit:
            questao.atividade = atividade
            questao.save()
            self.save_m2m()
        self.alternativas.save(commit, questao)
        return questao

    def has_changed(self):
        return super().has_changed() or self.alternativas.has_changed()


class BaseQuestaoFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        acao = self.data.get('acao')
        if acao == 'questao-adicionar':
            self.forms[-1].fields['comando'].widget.attrs.update({
                'autofocus': True
            })

    def save(self, commit=True, atividade=None):
        questoes = super().save(commit=False)
        if commit:
            for form in self.saved_forms:
                form.save(atividade=atividade)

            for form in self.deleted_forms:
                if not form.instance.pk:
                    continue
                self.deleted_objects.append(form.instance)
                form.instance.delete()
        return questoes

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if index > 0:
            form.fields.move_to_end('DELETE', last=False)
        else:
            form.fields.pop('DELETE')


QuestaoFormSet = forms.modelformset_factory(
    models.Questao,
    form=QuestaoForm,
    formset=BaseQuestaoFormSet,
    can_delete=True,
    min_num=1,
    extra=0
)


class AtividadeForm(ModelForm):
    inicio = DateTimeField()
    fim = DateTimeField()

    class Meta:
        model = models.Atividade
        fields = ['assunto', 'inicio', 'fim', 'n_grupos', 'n_membros', 'turmas']
        widgets = {
            'turmas': CheckboxSelectMultiple('turma', 'f'),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance']:
            kwargs['instance'].inicio = fix_date(kwargs['instance'].inicio)
            kwargs['instance'].fim = fix_date(kwargs['instance'].fim)

        kwargs['use_required_attribute'] = False
        super().__init__(*args, **kwargs)

        acao = self.data.get('acao', '')

        self.questoes = QuestaoFormSet(
            data=self.data or None,
            prefix="questao",
            queryset=self.instance.questoes.all()
        )

        quant_questoes = self.questoes.total_form_count()
        for n, questao_form in enumerate(self.questoes, start=1):
            data = self.data or None
            if acao == 'questao-adicionar' and n == quant_questoes:
                data = None

            questao_form.alternativas = AlternativaFormSet(
                data=data,
                prefix="alternativa-q%d" % n,
                queryset=questao_form.instance.alternativas.all()
            )

        if acao == '':
            self.fields['assunto'].widget.attrs.update({'autofocus': True})

    def is_valid(self):
        return super().is_valid() and self.questoes.is_valid()

    def save(self, commit=True):
        atividade = super().save(commit)
        self.questoes.save(commit=commit, atividade=atividade)
        return atividade

    def has_changed(self):
        return super().has_changed() or self.questoes.has_changed()


class GrupoForm(forms.ModelForm):
    class Meta:
        model = models.Grupo
        fields = ['membros']
        widgets = {
            'membros': CheckboxSelectMultiple(
                'usuario sem grupo para essa atividade', 'm'
            )
        }


class GrupoCriacaoForm(GrupoForm):
    def __init__(self, atividade, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['membros'].queryset = models.Usuario.objects.exclude(
            Q(groups__name__startswith="P") | Q(grupo__atividade=atividade))
        self.instance.atividade = atividade


class GrupoEdicaoForm(GrupoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            grupo = self.instance
            self.fields['membros'].queryset = models.Usuario.objects.exclude(
                Q(groups__name__startswith="P") |
                (Q(grupo__atividade=grupo.atividade) &
                    ~Q(grupo__id=grupo.id)))


class RespostaForm(forms.Form):
    def __init__(self, resposta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resposta = resposta
        self.fields['alternativas'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=self.alternativas,
            error_messages={
                'required': 'Não esqueça de responder essa questão!',
            }
        )
        try:
            self.fields['alternativas'].initial = resposta.escolha.id
            if resposta.enviada:
                self.fields['alternativas'].widget.attrs['disabled'] = True
        except AttributeError:
            pass

    @property
    def alternativas(self):
        return [(alternativa.id, alternativa.texto)
                for alternativa in self.resposta.questao.alternativas.all()]

    def save(self, enviar=False):
        self.resposta.escolha_id = self.cleaned_data['alternativas']
        if enviar:
            self.resposta.enviada = True
        return self.resposta.save()


class BaseRespostaFormSet(forms.BaseFormSet):
    def __init__(self, grupo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grupo = grupo
        self.questoes = grupo.atividade.questoes.all()

    def save(self):
        acao = self.data.get('acao')
        respostas = []
        for form in self.forms:
            respostas.append(form.save(enviar=(acao == 'enviar')))
        return respostas

    def get_form_kwargs(self, index):
        form_kwargs = super().get_form_kwargs(index)
        form_kwargs['resposta'], created = models.Resposta.objects.get_or_create(
            grupo=self.grupo,
            questao=self.questoes[index]
        )
        return form_kwargs


RespostaFormSet = forms.formset_factory(
    form=RespostaForm,
    formset=BaseRespostaFormSet,
    min_num=1,
    extra=0
)
