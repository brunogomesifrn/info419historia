from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define o manager do model Usuario sem o campo username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Cria e salva um Usuario com o email e a senha dados."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um Usuario normal com o email e a senha dados."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Cria e salva um SuperUsuario com o email e a senha dados."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Model de usuário."""
    username = None  # O campo username não existirá nese model
    nome = models.CharField('Nome', max_length=50)
    email = models.EmailField('Email', unique=True)
    sobrenome = models.CharField('Sobrenome', max_length=50)
    matricula = models.CharField('Matrícula', max_length=14)
    professor = models.BooleanField('Professor')

    USERNAME_FIELD = 'email'  # Define o campo usado na autenticação
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.nome + ' ' + self.sobrenome


# class Perfil(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
#     nome = models.CharField('Nome', max_length=50)
#     sobrenome = models.CharField('Sobrenome', max_length=50)
#     matricula = models.CharField('Matrícula', max_length=14)
#     professor = models.BooleanField('Professor')

#     def __str__(self):
#         return self.nome + ' ' + self.sobrenome


class Turma(models.Model):
    nome = models.CharField('Nome', max_length=50)
    membros = models.ManyToManyField(Usuario)

    def __str__(self):
        return self.nome


class Atividade(models.Model):
    assunto = models.CharField('Assunto', max_length=50)
    peso = models.IntegerField('Peso')
    inicio = models.DateTimeField('Início')
    fim = models.DateTimeField('Fim')
    turmas = models.ManyToManyField(Turma)

    def __str__(self):
        return self.assunto


# class Grupo(models.Model):
#     nota = models.IntegerField('Nota', null=True, blank=True)
#     membros = models.ManyToManyField(
#         Usuario, limit_choices_to={'professor': False})
#     atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)


class Tipo(models.Model):
    nome = models.CharField('Tipo', max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Documento(models.Model):
    titulo = models.CharField('Título', max_length=100)
    origem = models.TextField('Origem')
    creditos = models.CharField('Créditos', max_length=100)
    texto = models.TextField('Texto', blank=True, null=True)
    arquivo = models.FileField(
        'Arquivo', upload_to='documentos', blank=True, null=True)
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT)

    def __str__(self):
        return self.titulo


class Questao(models.Model):
    comando = models.TextField('Comando')
    peso = models.IntegerField('Peso')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    documentos = models.ManyToManyField(Documento)


class Alternativa(models.Model):
    texto = models.TextField('Texto')
    peso = models.IntegerField('Peso')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)

    def __str__(self):
        return self.texto
