from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property
from datetime import timedelta

GRUPO_PROFESSOR = Group.objects.get_or_create(name='Professor')


class UserManager(BaseUserManager):
    """Define o manager do model Usuario sem o campo username."""

    use_in_migrations = True

    def _create_user(self, email, password, professor, **extra_fields):
        """Cria e salva um Usuario com o email e a senha dados."""
        if not extra_fields.get('nome'):
            raise ValueError('Um usuário deve possuir um nome')
        if not extra_fields.get('sobrenome'):
            raise ValueError('Um usuário deve possuir um sobrenome')
        if not extra_fields.get('matricula'):
            raise ValueError('Um usuário deve possuir uma matrícula')
        if not email:
            raise ValueError('Um usuário deve possuir um email')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if professor:
            user.groups.add(GRUPO_PROFESSOR)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um Usuario normal com o email e a senha dados."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('professor', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Cria e salva um SuperUsuario com o email e a senha dados."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Um superusuário deve ter is_staff=True.')
        if extra_fields.get('professor') is not True:
            raise ValueError('Um superusuário deve ter professor=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Um superusuário deve ter is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Model que representa um usuário."""
    username = None  # O campo username não existirá nese model.
    nome = models.CharField('Nome', max_length=50)
    email = models.EmailField('Email', unique=True)
    sobrenome = models.CharField('Sobrenome', max_length=50)
    matricula = models.CharField('Matrícula', max_length=14, unique=True)

    USERNAME_FIELD = 'email'  # Define o campo usado na autenticação.
    REQUIRED_FIELDS = ['nome', 'sobrenome', 'matricula']

    objects = UserManager()  # Sobreescrevendo o manager de usuário.

    def __str__(self):
        """Retorna a represetação do model Usuario como string."""
        return self.nome + ' ' + self.sobrenome + ' (' + self.matricula + ')'

    @cached_property
    def nome_completo(self):
        """Retorna o nome completo de um usuário."""
        return self.nome + ' ' + self.sobrenome

    @cached_property
    def is_professor(self):
        """Checa se o usúario é professor."""
        return self.groups.filter(pk=GRUPO_PROFESSOR.pk).exists()

    def get_participacao(self, atividade):
        """
        Retorna o objeto do model Particapao vinculado ao usuário e
        a uma certa atividade; se ele não existir, None é retornado.
        """
        try:
            return self.participacoes.get(grupo__atividade=atividade)
        except ObjectDoesNotExist:
            return None


class Turma(models.Model):
    """Model que representa turma."""
    nome = models.CharField('Nome', max_length=50, unique=True)
    membros = models.ManyToManyField(Usuario)

    class Meta:
        ordering = ('nome',)

    def __str__(self):
        """Retorna a represetação do model Turma como string."""
        return self.nome


class TipoDocumento(models.Model):
    """Model que representa um tipo de documento."""
    nome = models.CharField('Nome', max_length=50, unique=True)

    def __str__(self):
        """Retorna a represetação do model TipoDocumento como string."""
        return self.nome


class Documento(models.Model):
    """Model que representa um documento."""
    titulo = models.CharField('Título', max_length=100)
    origem = models.TextField('Origem')
    creditos = models.CharField('Créditos', max_length=100)
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)

    def __str__(self):
        """Retorna a represetação do model Documento como string."""
        return self.titulo

    @cached_property
    def texto(self):
        """
        Retorna o texto correspondente a esse
        documento ou None, se ele não existir.
        """
        try:
            return self.documento_texto.texto
        except ObjectDoesNotExist:
            return None

    @cached_property
    def arquivo(self):
        """
        Retorna o arquivo correspondente a esse
        documento ou None, se ele não existir.
        """
        try:
            return self.documento_arquivo.arquivo
        except ObjectDoesNotExist:
            return None


class DocumentoTexto(models.Model):
    """Model que representa um texto de um documento."""
    documento = models.OneToOneField(Documento,
                                     on_delete=models.CASCADE)
    texto = models.TextField('Texto')

    class Meta:
        default_related_name = "documento_texto"

    def __str__(self):
        """Retorna a represetação do model DocumentoTexto como string."""
        return self.texto


class DocumentoArquivo(models.Model):
    """Model que representa um arquivo de um documento."""
    documento = models.OneToOneField(Documento,
                                     on_delete=models.CASCADE)
    arquivo = models.FileField('Arquivo', upload_to='documentos')

    class Meta:
        default_related_name = "documento_arquivo"

    def __str__(self):
        """Retorna a represetação do model DocumentoArquivo como string."""
        return self.arquivo


class Atividade(models.Model):
    """Model que representa uma atividade."""
    assunto = models.CharField('Assunto', max_length=50)
    inicio = models.DateTimeField('Início')
    fim = models.DateTimeField('Fim')
    turmas = models.ManyToManyField(Turma)
    n_grupos = models.IntegerField("Número máximo de grupos")
    n_membros = models.IntegerField("Número máximo de membros em um grupo")

    def __str__(self):
        """Retorna a represetação do model Atividade como string."""
        return self.assunto

    def aceita_grupos(self):
        """Checa se atividade ainda suporta a criação de novos grupos."""
        return self.grupos.count() < self.n_grupos

    def clean(self, *args, **kwargs):
        """Checa se existe algum erro numa instância de Atividade."""

        # Checando se o fim da atividade está a pelo menos 45 minutos
        # depois do seu início.
        if self.fim < self.inicio + timedelta(minutes=45):
            raise ValidationError({
                'fim': """O fim da atividade deve vir pelo
                          menos 45 minutos depois do início"""
            })
        super().clean(*args, **kwargs)


class Questao(models.Model):
    """Model que representa uma questão."""
    comando = models.TextField('Comando')
    peso = models.IntegerField('Peso')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    documentos = models.ManyToManyField(Documento)

    class Meta:
        default_related_name = 'questoes'

    def __str__(self):
        """Retorna a represetação do model Questao como string."""
        return self.comando


class Alternativa(models.Model):
    """Model que representa uma alternativa."""
    texto = models.TextField('Texto')
    peso = models.IntegerField('Peso')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'alternativas'

    def __str__(self):
        """Retorna a represetação do model Alternativa como string."""
        return self.texto


class Grupo(models.Model):
    """Model que representa um grupo."""
    nota = models.IntegerField('Nota', null=True, blank=True)
    membros = models.ManyToManyField(
        Usuario,
        through='Participacao'
    )
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "grupos"

    def __str__(self):
        """Retorna a represetação do model Grupo como string."""
        return "Grupo de %s" % self.criador.nome

    def clean(self, *args, **kwargs):
        """Checa se existe algum erro numa instância de Grupo."""

        # Checando se a atividade vinculada ao grupo ainda aceita grupo.
        if not self.atividade.aceita_grupos:
            raise ValidationError({
                'atividade': "A atividade \"%s\" só pode ter %d grupos" % (
                    self.atividade, self.atividade.n_grupos
                )
            })
        super().clean(*args, **kwargs)

    @cached_property
    def criador(self):
        """Retorna o usuário criador do grupo."""
        try:
            return self.participacoes.get(criador=True).aluno
        except ObjectDoesNotExist:
            return None

    @cached_property
    def pendencias(self):
        """Retorna as participações ainda não confirmadas do grupo."""
        return self.participacoes.filter(confirmado=False)


class Participacao(models.Model):
    """Model que representa uma partipação num grupo."""
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    aluno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    criador = models.BooleanField(default=False)
    confirmado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('grupo', 'aluno')
        ordering = ('criador',)
        default_related_name = 'participacoes'

    def clean(self, *args, **kwargs):
        """Checa se existe algum erro numa instância de Participacao."""

        # Checando se o usuário vinculado à participação é um professor.
        if self.aluno.is_professor:
            raise ValidationError({
                'aluno': "Um professor não pode fazer parte de um grupo"
            })

        # Checando se o grupo vinculado à participação já tem um criador.
        if self.criador and self.grupo.criador:
            raise ValidationError({
                'criador': "O grupo só pode ter um criador"
            })

        # Checando se o usuário vinculado à participação
        # já tem um grupo para essa atividade.
        if self.aluno.get_participacao(self.grupo.atividade):
            raise ValidationError({
                'aluno': "%s já tem um grupo para a atividade \"%s\""
                % (self.aluno, self.grupo.atividade)
            })

        super().clean(*args, **kwargs)


class Resposta(models.Model):
    """Model que representa uma resposta."""
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    questao = models.ForeignKey(
        Questao,
        on_delete=models.CASCADE,
        limit_choices_to={
            'atividade': models.F('grupo__atividade')
        }
    )
    escolha = models.ForeignKey(
        Alternativa,
        on_delete=models.PROTECT,
        limit_choices_to={
            'questao': models.F('questao')
        },
        null=True
    )
    enviada = models.BooleanField('Enviada', default=False)

    class Meta:
        unique_together = ('grupo', 'questao')
